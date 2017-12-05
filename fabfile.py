from datetime import datetime
from hashlib import md5
from fabric.api import run, local, env, get, put, runs_once, execute

PROJECT = 'telenot'


def init():
    run(f'mkdir -p ~/{PROJECT}/images ~/{PROJECT}/data')


def image_hash():
    hsh = md5()
    hsh.update(open('docker/Dockerfile', 'rb').read())
    hsh.update(open('requirements.txt', 'rb').read())
    return hsh.hexdigest()[:10]


@runs_once
def prepare_image():
    hsh = image_hash()
    local(f'''
        docker inspect {PROJECT}:{hsh} > /dev/null || docker build -t {PROJECT}:{hsh} docker
        docker save {PROJECT}:{hsh} | gzip -1 > /tmp/image.tar.gz
    ''')


def push_image():
    hsh = image_hash()
    execute(prepare_image)
    local(f'rsync -P /tmp/image.tar.gz {env.host}:{PROJECT}/images/{hsh}.tar.gz')
    run(f'docker load -i {PROJECT}/images/{hsh}.tar.gz')


def backup(fname=f'/tmp/{PROJECT}-backup.tar.gz'):
    run(f'tar -C {PROJECT}/data -czf /tmp/backup.tar.gz .')
    get('/tmp/backup.tar.gz', fname)


def restore(fname=f'/tmp/{PROJECT}-backup.tar.gz'):
    put(fname, '/tmp/backup.tar.gz')
    run(f'tar -C {PROJECT}/data xf /tmp/backup.tar.gz .')


@runs_once
def pack_backend():
    hsh = image_hash()
    local(f'''
        echo {hsh} > image_hash
        ( git ls-files && echo image_hash ) | tar cz -f /tmp/backend.tar.gz -T -
     ''')


def upload():
    version = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    execute(pack_backend)
    put('/tmp/backend.tar.gz', PROJECT)
    run(f'''
        cd {PROJECT}
        mkdir app-{version}
        tar -C app-{version} -xf backend.tar.gz
        ln -snf app-{version} app
    ''')


def restart():
    run(f'''
        docker stop -t 10 {PROJECT}-http
        docker rm {PROJECT}-http || true
        cd {PROJECT}
        docker run -d --name {PROJECT}-http -e CONFIG=/data/config.py \\
                   -v $PWD/app:/app -v $PWD/data:/data -w /app -u $UID \\
                   {PROJECT}:`cat app/image_hash` uwsgi --ini /app/uwsgi.ini
        docker logs --tail 10 {PROJECT}-http
    ''')
