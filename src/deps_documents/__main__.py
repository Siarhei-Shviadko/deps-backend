import click


@click.group()
def cli() -> None:
    pass


@cli.command()
def serve() -> None:
    from deps_documents.web import run_app

    run_app()


@cli.command()
def consume() -> None:
    from deps_documents.app import run_consumer

    run_consumer()


if __name__ == "__main__":
    cli()
