from fastapi import FastAPI, HTTPException
import xml.etree.ElementTree as ET
import httpx
import base64

app = FastAPI()


async def get_basic_auth_header(username: str, password: str):
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
    return {"Authorization": f"Basic {encoded_credentials}"}

async def get_calendar_id(username: str, password: str):
    url = f"https://calendar.nailsbot.ru/{username}/"
    headers = {'ContentType': "text/plain;charset=UTF-8",
               **await get_basic_auth_header(username, password)}
    async with httpx.AsyncClient() as client:
        response = await client.request("PROPFIND", url, headers=headers)
        # return response
        xml_content = await response.text()

        # Парсинг XML
        root = ET.fromstring(xml_content)
        namespaces = {
            'DAV': 'DAV:',
            'C': 'urn:ietf:params:xml:ns:caldav',
            'CR': 'urn:ietf:params:xml:ns:carddav',
            'ICAL': 'http://apple.com/ns/ical/',
            'RADICALE': 'http://radicale.org/ns/',
            'ns3': 'http://inf-it.com/ns/ab/'
        }

        # Находим первый <href> внутри первого <response>
        first_response = root.find("DAV:response", namespaces)
        if first_response is not None:
            first_href = first_response.find("DAV:href", namespaces)
            if first_href is not None:
                return first_href.text
        return None

@app.post("/add_event")
async def add_event(event_data: str, username: str, password: str):
    calendar_id = await get_calendar_id(username, password)
    url = f"https://calendar.nailsbot.ru/{calendar_id}/"
    headers = {
        "Content-Type": "text/calendar",
        **await get_basic_auth_header(username, password)
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(url, headers=headers, data=event_data)
            if response.status_code == 201:
                return {"message": "Event added successfully"}
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to add event")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/delete_event")
async def delete_event(calendar_id: str, event_id: str, username: str, password: str):
    url = f"https://calendar.nailsbot.ru/{calendar_id}/event.ics"
    headers = get_basic_auth_header(username, password)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=headers)
            if response.status_code == 204:
                return {"message": "Event deleted successfully"}
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to delete event")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/hello')
async def read_root():
    return {'message': 'Hello, World!'}
