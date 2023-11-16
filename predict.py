# Prediction interface for Cog ⚙️
# https://github.com/replicate/cog/blob/main/docs/python.md

from cog import BasePredictor, Input, Path
import subprocess
import os
import time
import random
import re


class Predictor(BasePredictor):
    def setup(self) -> None:
        """Load the model into memory to make running multiple predictions efficient"""
        self.tailscale = subprocess.Popen(
            [
                "tailscaled",
                "--tun=userspace-networking",
                "--socks5-server=localhost:1055",
            ],
        )
        print("setup complete")
        self.file = "kill.txt"
    def predict(
        self,
        tailscale: str = Input(
            description="tailscale token",
        ),
        hostname: str = Input(
            description="tailscale hostname (optional)", default=str(random.randint(0,100000))
        ),
    ) -> Path:
        """Run a single prediction on the model"""
        print("launching tailscale")
        up = ["tailscale", "up", "-ssh", "--authkey", tailscale]
        if hostname:
            up.append("--hostname")
            up.append(hostname)
        subprocess.check_call(up)
        # HTTPS to allow camera access - but max of 10 registrations per IP in 3 hours, with no obvious error message from tailscale cert
        # try:
        #     _, _ = subprocess.check_output(["tailscale", "cert"], stderr=subprocess.STDOUT)
        # except subprocess.CalledProcessError as e:
        #     # Don't worry, we expect an error - we're just using the output to get the domain.
        #     # TODO: Probably a better way to get this
        #     out = str(e.output)
        # pattern = r'For domain, use "(.*?)"'
        # domain = re.search(pattern, out).group(1)
        # print(domain)
        # print(subprocess.check_output(['whoami']))
        # subprocess.check_output(["tailscale", "cert", "--cert-file=cert.pem", "--key-file=key.pem", domain])
        # subprocess.check_output('cd /src && uvicorn "app-controlnet:app" --host 0.0.0.0 --port 7860 --reload --ssl-certfile=cert.pem --ssl-keyfile=key.pem', shell=True)
        subprocess.check_output('cd /src && uvicorn "app-controlnet:app" --host 0.0.0.0 --port 7860 --reload', shell=True)

        with open(self.file, "w") as f:
            f.write("zzz")

        print("sleepy time")
        while os.path.exists(self.file):
            time.sleep(1)

        print("turning off tailscale")
        subprocess.check_call(["tailscale", "down", "--accept-risk", "all"])

        print("all done")

        return []