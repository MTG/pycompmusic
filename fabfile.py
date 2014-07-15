from fabric.api import env, roles, run, cd

env.roledefs["web"] = ["sitar.s.upf.edu"]
env.use_ssh_config = True
env.forward_agent = True

@roles("web")
def updatedocs():
    """Update the docs"""

    with cd("/srv/dunya/env/src/pycompmusic"):
        run("git pull", pty=False)
        run("make html", pty=False)

