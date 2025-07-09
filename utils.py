def format_cme_event(event):
    return {
        "Start Time": event.get("startTime"),
        "Source Location": event.get("sourceLocation"),
        "Note": event.get("note"),
        "Link": event.get("link"),
    }
