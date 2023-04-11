import nox

@nox.session(python=["3"])
def tests(session):
    session.install("-r", "requirements.txt")
    session.install("pytest")
    session.run("pytest", "tests")
