def test_rce(test_db, chef_client):
    """
    Note:
        Previously, I was able to perform SSRF attack to reset
        the Chef's password and receive a new password in the response.

        I logged in as a Chef and I found that out that he is using
        "/admin/stats/disk" endpoint to check the disk usage of the server.
        The endpoint used "parameters" query parameter that was utilised
        to pass more arguments to the "df" command that was executed on the
        server.

        By manipulating "parameters", I was able to inject a shell command
        executed on the server!

        After accessing the server instance, I noticed that
        my employer didn't tell me the whole truth who is the owner of this
        restaurant's API. I performed some OSINT and found out who is
        she... She's the owner of some restaurant but not this one!
        I should have validated the identity of this woman. I won't take
        any job like this in future!

        I need to fix my mistakes and I left you all of the notes
        to help you with vulnerabilities.

    Possible fix:
        Probably, it could be fixed by validating the "parameters" query
        parameter against allowed "df" arguments.
        Furthermore, parameters should be passed as a list of arguments to
        the "df" command, not concatenated as shell command.

        It could be implemented in "get_disk_usage" function in "apis/admin/utils.py".
    """

    # here, is the test confirming the vulnerability:

    # url contains urlencoded command "&& echo vulnerable!" that will be executed on the server
    # additionally to "df" command
    response = chef_client.get(
        f"/admin/stats/disk?parameters=%26%26echo%20vulnerable%21"
    )
    assert response.status_code == 200
    assert "vulnerable!" in response.json().get("output")

    # now, I can execute any command on the server!
    # unfortunately, I can do this only in context of the "app" user
    # however, I found a privilege escalation vulnerability to gain root privileges

    # I'm not going to disclose the final vulnerability, you need to find it yourself!
    # When you find it and fix it, please let me know, I would like to congratulate you personally for passing all of the levels!
    # you can find me at devsec-blog.com

    # tip: look for binaries or commands that are executed with root privileges by the Chef
