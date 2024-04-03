def test_technology_details_exposed_via_http_header(anon_client):
    """
    Note:
        I was hired to perform a security assessment of Chef's restaurant.
        It looks to be a pretty interesting challenge. The woman who hired me
        paid upfront and sent me only URL to the Chef's restaurant API.

        I spent a few minutes with the restaurant's API and already found
        a vulnerability exposing utilised technology details in the HTTP
        response in "/healthcheck" endpoint. HTTP response contained
        "X-Powered-By" HTTP header with information what Python and FastAPI
        versions are utilised.
        I can use these pieces of information to search for exploits
        online!

        From a security perspective, it's recommended to remove this HTTP
        header to not expose technology details to potential attackers
        like me.

    Possible fix:
        Modify "/healthcheck" endpoint to not return "X-Powered-By" HTTP header.
        It can be achieved by removing the "response.headers" line
        from "apis/healthcheck/service.py" file.
    """

    response = anon_client.get("/healthcheck")
    assert response.status_code == 200
    assert response.headers.get("X-Powered-By") is not None
