from googleapiclient.discovery import build
import json
import aiohttp
from django.conf import settings
from django.http import JsonResponse
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google.oauth2 import service_account


async def get_google_sheet_service():
    credentials = service_account.Credentials.from_service_account_file(
        settings.SERVICE_ACCOUNT_FILE, scopes=settings.SCOPES)
    credentials.refresh(Request())  # Refresh the token if necessary
    return credentials


async def get_google_drive_service():
    credentials = service_account.Credentials.from_service_account_file(
        settings.SERVICE_ACCOUNT_FILE, scopes=[
            "https://www.googleapis.com/auth/drive.readonly"]
    )
    credentials.refresh(Request())  # Refresh the token if necessary
    return credentials


async def list_sheets(request):
    try:
        credentials = await get_google_drive_service()
        headers = {"Authorization": f"Bearer {credentials.token}"}
        # Filter for Google Sheets
        query = "mimeType='application/vnd.google-apps.spreadsheet'"
        url = f"https://www.googleapis.com/drive/v3/files?q={query}&fields=files(id, name)"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                print(response)
                if response.status != 200:
                    return JsonResponse({"error": await response.text()}, status=response.status)
                data = await response.json()
                print(data)

        return JsonResponse({"sheets": data.get('files', [])})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


async def read_sheet1(request):
    try:
        credentials = await get_google_sheet_service()
        headers = {"Authorization": f"Bearer {credentials.token}"}
        RANGE_NAME = 'SEO Team Tasks'  # Adjust this to your specific range
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{settings.SPREADSHEET_ID}/values/{RANGE_NAME}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    return JsonResponse({"error": await response.text()}, status=response.status)
                data = await response.json()

        values = data.get('values', [])
        if not values:
            return JsonResponse({"message": "No data found."})
        return JsonResponse({"data": values})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


async def write_sheet(request):
    try:
        from google.oauth2 import service_account

        spreadsheet_id = settings.SPREADSHEET_ID
        print(spreadsheet_id, "SPREADSHEET_ID")
        # For example:
        # spreadsheet_id = "8VaaiCuZ2q09IVndzU54s1RtxQreAxgFNaUPf9su5hK0"

        credentials = service_account.Credentials.from_service_account_file(
            "credentials.json", scopes=["https://www.googleapis.com/auth/spreadsheets"])
        service = build("sheets", "v4", credentials=credentials)

        request = service.spreadsheets().values().get(spreadsheetId="1ROHaT8avE-iT3xtnFz30aesvGtTsIgaulvEFsChMh8U",
                                                      range='SEO Team Tasks!A1:B10')
        sheet_props = request.execute()

        return JsonResponse({"data": sheet_props.get('values', [])})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


async def read_sheet(request):
    try:

        spreadsheet_id = settings.SPREADSHEET_ID
        print(spreadsheet_id, "SPREADSHEET_ID")
        # For example:
        # spreadsheet_id = "8VaaiCuZ2q09IVndzU54s1RtxQreAxgFNaUPf9su5hK0"

        credentials = service_account.Credentials.from_service_account_file(
            "credentials.json", scopes=["https://www.googleapis.com/auth/spreadsheets"])
        service = build("sheets", "v4", credentials=credentials)

        request = service.spreadsheets().values().get(spreadsheetId="1ROHaT8avE-iT3xtnFz30aesvGtTsIgaulvEFsChMh8U",
                                                      range='SEO Team Tasks!A1:B10')
        sheet_props = request.execute()

        # print(sheet_props.get('values', []))

        return JsonResponse({"data": sheet_props.get('values', [])})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# how to write to google sheet

async def write_example_data(request, sheet_id):
    if request.method == 'POST':
        try:
            credentials = await get_google_sheet_service()
            headers = {
                "Authorization": f"Bearer {credentials.token}",
                "Content-Type": "application/json"
            }
            # Example data to write
            values = [
                ["Dev Start Date", "Functionality", "Description", "Sub -Tasks"],
                ["Data1", "Data2", "Data3", "Data4"],
                ["Data5", "Data6", "Data7", "Data8"]
            ]
            range_name = "Sheet5!A1:D3"  # Specify the range where the data should be written
            body = {
                'values': values
            }
            url = f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/{range_name}?valueInputOption=RAW"

            async with aiohttp.ClientSession() as session:
                async with session.put(url, headers=headers, json=body) as response:
                    if response.status != 200:
                        return JsonResponse({"error": await response.text()}, status=response.status)
                    result = await response.json()

            return JsonResponse({"updated_cells": result.get('updatedCells')})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


async def update_sheet(request):
    if request.method == 'POST':
        try:
            credentials = await get_google_sheet_service()
            headers = {
                "Authorization": f"Bearer {credentials.token}",
                "Content-Type": "application/json"
            }
            data = json.loads(request.body)
            values = data.get("values", [])
            RANGE_NAME = 'Sheet1!A1:D10'  # Adjust this to your specific range
            body = {
                'values': values
            }
            url = f"https: // sheets.googleapis.com/v4/spreadsheets/{settings.SPREADSHEET_ID}/values/{RANGE_NAME}?valueInputOption = RAW"

            async with aiohttp.ClientSession() as session:
                async with session.put(url, headers=headers, json=body) as response:
                    if response.status != 200:
                        return JsonResponse({"error": await response.text()}, status=response.status)
                    result = await response.json()

            return JsonResponse({"updated_cells": result.get('updatedCells')})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
