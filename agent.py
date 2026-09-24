import json


def load_services():
    with open("services.json", "r") as file:
        return json.load(file)


def get_service_information(user_request):
    services = load_services()

    for service in services["services"]:
        if service["name"].lower() in user_request.lower():
            return service

    return None
