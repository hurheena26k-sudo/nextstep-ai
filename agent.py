
import json


def load_services():
    with open("services.json", "r") as file:
        return json.load(file)


def prepare_request(user_request):
    services = load_services()

    return {
        "user_request": user_request,
        "available_services": services["services"]
    }
