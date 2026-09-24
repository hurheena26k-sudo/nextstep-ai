import json


def load_services():
    with open("services.json", "r") as file:
        return json.load(file)


def get_service_information(user_request):
    services = load_services()
    request = user_request.lower().strip()

    for service in services["services"]:

        service_name = service["name"].lower()

        if service_name in request:
            return service

        keywords = service.get("keywords", [])

        for keyword in keywords:
            if keyword.lower() in request:
                return service

    return None


def detect_intent(user_request, service):
    request = user_request.lower().strip()
    service_name = service["name"]

    # Property Tax
    if service_name == "Property Tax":

        if any(word in request for word in [
            "pay",
            "payment",
            "paying"
        ]):
            return "payment"

        if any(word in request for word in [
            "check",
            "details",
            "status",
            "amount"
        ]):
            return "checking tax details"

        return "general information"

    # Birth Certificate
    if service_name == "Birth Certificate":

        if any(word in request for word in [
            "apply",
            "get",
            "obtain",
            "request"
        ]):
            return "application"

        return "general information"

    # Municipal Complaint
    if service_name == "Municipal Complaint":

        if any(word in request for word in [
            "complaint",
            "complain",
            "report",
            "grievance"
        ]):
            return "submit complaint"

        return "general information"

    return "general information"
