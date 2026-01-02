import argparse

def pre_parse_arg():
    p = argparse.ArgumentParser()
    p.add_argument("--debug", action="store_true")
    r =p.parse_known_args()
    return r[0]

def parse_arg():
    p = argparse.ArgumentParser()
    p.add_argument("filename", type=argparse.FileType("rb"))
    p.add_argument("--debug", action="store_true")
    return p.parse_args()
