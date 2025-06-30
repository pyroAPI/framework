
import typer
import uvicorn

cli = typer.Typer()

@cli.command()
def runserver(host: str = "127.0.0.1", port: int = 8000):
    """Run the server using Uvicorn."""
    uvicorn.run("main:app", host=host, port=port, reload=True)

@cli.command()
def hello():
    print("Hello from PyroAPI!")
