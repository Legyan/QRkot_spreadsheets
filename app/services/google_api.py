from datetime import datetime

from aiogoogle import Aiogoogle

from app.core.config import settings
from app.services.constants import FORMAT, REPORT_TABLE


async def spreadsheets_create(wrapper_services: Aiogoogle) -> str:
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    spreadsheet_body = {
        'properties': {'title': f'Отчет на {now_date_time}',
                       'locale': 'ru_RU'},
        'sheets': [{'properties': {'sheetType': 'GRID',
                                   'sheetId': 0,
                                   'title': 'Лист1',
                                   'gridProperties': {'rowCount': 100,
                                                      'columnCount': 11}}}]
    }
    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)
    )
    spreadsheetid = response['spreadsheetId']
    return spreadsheetid


async def set_user_permissions(
        spreadsheetid: str,
        wrapper_services: Aiogoogle
) -> None:
    permissions_body = {'type': 'user',
                        'role': 'writer',
                        'emailAddress': settings.email}
    service = await wrapper_services.discover('drive', 'v3')
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheetid,
            json=permissions_body,
            fields="id"
        ))


async def spreadsheets_update_value(
        spreadsheetid: str,
        projects: list,
        wrapper_services: Aiogoogle
) -> None:
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    table_values = [
        [REPORT_TABLE['A1'], now_date_time],
        [REPORT_TABLE['A2']],
        [REPORT_TABLE['A3'], REPORT_TABLE['B3'], REPORT_TABLE['C3']],
    ]
    for project in projects:
        new_row = [
            str(project.name),
            str(project.close_date - project.create_date),
            str(project.description)
        ]
        table_values.append(new_row)

    update_body = {
        'majorDimension': 'ROWS',
        'values': table_values
    }
    rows_len = len(table_values)
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheetid,
            range=f'A1:C{rows_len}',
            valueInputOption='USER_ENTERED',
            json=update_body
        )
    )
