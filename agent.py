import json


def load_services():
    with open("services.json", "r") as file:
        return json.load(file)


def get_service_information(user_request):
    services = load_services()

    request = user_request.lower()

    for service in services["services"]:
        service_name = service["name"].lower()

        if service_name in request:
            return service

    return None
