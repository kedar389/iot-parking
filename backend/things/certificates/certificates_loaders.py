import sys


def get_ssl_parameters() -> dict:
    try:
        certificate_path = "baltimore.cer"
        print('Loading Blatimore Certificate')
        with open(certificate_path, 'r') as f:
            cert = f.read()
        print('Obtained Baltimore Certificate')
        return {'cert': cert}
    except Exception:
        print("Baltimore Certificate could not be loaded!")
        sys.exit(1)  # TODO CHECK
