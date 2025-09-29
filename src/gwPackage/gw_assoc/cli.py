import click
from .association import Association

@click.command()
@click.option("--gw-file", type=str, required=True)
@click.option("--transient-file", type=str, required=True)
def main(gw_file, transient_file):
    import json
    transient = json.load(open(transient_file))
    assoc = Association(gw_file, transient)
    results = assoc.compute_odds()
    print("Posterior odds:", results)
    assoc.plot("skymap.png")

if __name__ == "__main__":
    main()
