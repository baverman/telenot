#!/usr/bin/env python
import sys
from datetime import datetime
from hashlib import md5
from textwrap import dedent

import mitogen.utils
from mitosys import shell, shellc, unarchive, put, Remote, symlink, write_data

PROJECT = 'telenot'
HTTP_PORT = 5000
CONFIG = '/data/config.py'


def init(remote):
    remote.shell(f'''
        mkdir -p ~/{PROJECT}/data ~/{PROJECT}/bin
    ''')
    put('etc/clean-expired', remote, f'{PROJECT}/bin/clean-expired', mode=0o755)
    put('etc/daemon.sh', remote, f'{PROJECT}/bin/daemon.sh', mode=0o755)


def image_hash():
    hsh = md5()
    hsh.update(open('docker/Dockerfile', 'rb').read())
    hsh.update(open('requirements.txt', 'rb').read())
    return hsh.hexdigest()[:10]


def build_image(hsh):
    return shell(f'''
        docker build -t {PROJECT}:{hsh} docker
        docker save {PROJECT}:{hsh} | gzip -1 > /tmp/image.tar.gz
    ''')


def ensure_image(remote):
    hsh = image_hash()
    if not remote.shell(f'docker inspect {PROJECT}:{hsh} > /dev/null', check=False):
        return

    build_image(hsh)

    @remote.run
    def _steps():
        print('Upload image')
        shell('docker load', input=open('/tmp/image.tar.gz', 'rb').read())


def upload(remote):
    version = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    hsh = image_hash()
    src_tar = shellc('git ls-files | tar -czT -')

    env_file = dedent(f'''\
        IMAGE="{PROJECT}:{hsh}"
        NAME="{PROJECT}-http"
        DOCKER_OPTS="-p {HTTP_PORT}:5000 -e CONFIG={CONFIG} \\
                     -v $PWD/app:/app -v $PWD/data:/data -w /app"
        CMD="uwsgi --ini /app/uwsgi.ini"
    ''')

    @remote.run
    def _steps():
        print(f'Uploading new version: {version}')
        unarchive(src_tar, f'{PROJECT}/app-{version}')
        symlink(f'app-{version}', f'{PROJECT}/app')
        write_data(env_file, f'{PROJECT}/app/docker.env')
        shell(f"python {PROJECT}/bin/clean-expired -c 10 -t 7 '{PROJECT}/app-*'")


def restart(remote):
    @remote.run
    def _steps():
        print('Restarting ...')
        shell(f'''
            cd {PROJECT}
            ./bin/daemon.sh app/docker.env
            echo "Latest logs:"
            timeout 3 docker logs --tail 10 -f {PROJECT}-http || true
        ''')


def deploy(remote):
    ensure_image(remote)
    upload(remote)
    restart(remote)


def main(router):
    task = sys.argv[1]
    host = router.ssh(hostname='pg.remote')
    remote = Remote(host)
    fn = globals()[task]
    fn(remote)


if __name__ == '__main__':
    mitogen.utils.log_to_file(level='INFO')
    mitogen.utils.run_with_router(main)
