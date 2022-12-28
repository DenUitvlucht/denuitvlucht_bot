
import os
import subprocess


def get_drankkot_snapshot(username: str, password: str, ipv4: str):

    output_path = os.path.join(os.getcwd(), 'denuitvlucht_bot', 'output', 'snapshot.png')

    command = [
        'ffmpeg',
        '-rtsp_transport',
        'tcp',
        '-i',
        f'rtsp://{username}:{password}@{ipv4}',
        '-frames:v',
        '1',
        '-s',
        '1920x1080',
        output_path
    ]

    subprocess.call(command)

    return output_path
