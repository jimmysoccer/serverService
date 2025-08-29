from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from bson import ObjectId
from ...models.personal_website.js_ih_models import JSIHRecordCreate, JSIHRecordResponse
from .js_ih_router import js_ih_router
from typing import List


@js_ih_router.post("/js-ih-1/add")
async def add_js_ih_record(record: JSIHRecordCreate, request: Request):
    """Add a new record to JS-IH-1 collection or update existing record for the same date"""
    try:
        # Convert string date to datetime
        date_obj = datetime.fromisoformat(record.date.replace("Z", "+00:00"))

        # Normalize the date to midnight (00:00:00) to ignore time component
        normalized_date = date_obj.replace(hour=0, minute=0, second=0, microsecond=0)

        # Create the document with normalized date
        document = {"date": normalized_date, "number": record.number}

        # Check if a record already exists for this date (ignoring time)
        existing_record = await request.app.state.js_ih_coll.find_one(
            {"date": normalized_date}
        )

        if existing_record:
            # Update existing record
            result = await request.app.state.js_ih_coll.replace_one(
                {"date": normalized_date}, document
            )

            if result.acknowledged:
                return JSONResponse(
                    status_code=200,
                    content={
                        "message": "Record updated successfully",
                        "id": str(existing_record["_id"]),
                        "updated": True,
                    },
                )
            else:
                return JSONResponse(
                    status_code=500, content={"message": "Failed to update record"}
                )
        else:
            # Insert new record
            result = await request.app.state.js_ih_coll.insert_one(document)

            if result.acknowledged:
                return JSONResponse(
                    status_code=200,
                    content={
                        "message": "Record added successfully",
                        "id": str(result.inserted_id),
                        "updated": False,
                    },
                )
            else:
                return JSONResponse(
                    status_code=500, content={"message": "Failed to add record"}
                )
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"message": f"Error adding/updating record: {str(e)}"},
        )


@js_ih_router.get("/js-ih-1/year/{year}")
async def get_js_ih_by_year(year: int, request: Request):
    """Get all records for a specific year"""
    try:
        # Create date range for the year
        start_date = datetime(year, 1, 1)
        end_date = datetime(year + 1, 1, 1)

        # Query the database
        cursor = request.app.state.js_ih_coll.find(
            {"date": {"$gte": start_date, "$lt": end_date}}
        ).sort("date", 1)

        records = []
        async for doc in cursor:
            records.append(
                {
                    "id": str(doc["_id"]),
                    "date": doc["date"].isoformat(),
                    "number": doc["number"],
                }
            )

        return JSONResponse(
            status_code=200,
            content={"year": year, "count": len(records), "records": records},
        )
    except Exception as e:
        return JSONResponse(
            status_code=400, content={"message": f"Error retrieving records: {str(e)}"}
        )


@js_ih_router.get("/js-ih-1/month/{year}/{month}")
async def get_js_ih_by_month(year: int, month: int, request: Request):
    """Get all records for a specific month"""
    try:
        # Create date range for the month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        # Query the database
        cursor = request.app.state.js_ih_coll.find(
            {"date": {"$gte": start_date, "$lt": end_date}}
        ).sort("date", 1)

        records = []
        async for doc in cursor:
            records.append(
                {
                    "id": str(doc["_id"]),
                    "date": doc["date"].isoformat(),
                    "number": doc["number"],
                }
            )

        return JSONResponse(
            status_code=200,
            content={
                "year": year,
                "month": month,
                "count": len(records),
                "records": records,
            },
        )
    except Exception as e:
        return JSONResponse(
            status_code=400, content={"message": f"Error retrieving records: {str(e)}"}
        )


@js_ih_router.get("/js-ih-1/week/{year}/{week}")
async def get_js_ih_by_week(year: int, week: int, request: Request):
    """Get all records for a specific week (ISO week number)"""
    try:
        # Calculate the start of the year
        year_start = datetime(year, 1, 1)

        # Find the first Monday of the year
        while year_start.weekday() != 0:  # Monday is 0
            year_start += timedelta(days=1)

        # Calculate the start of the specified week
        week_start = year_start + timedelta(weeks=week - 1)
        week_end = week_start + timedelta(weeks=1)

        # Query the database
        cursor = request.app.state.js_ih_coll.find(
            {"date": {"$gte": week_start, "$lt": week_end}}
        ).sort("date", 1)

        records = []
        async for doc in cursor:
            records.append(
                {
                    "id": str(doc["_id"]),
                    "date": doc["date"].isoformat(),
                    "number": doc["number"],
                }
            )

        return JSONResponse(
            status_code=200,
            content={
                "year": year,
                "week": week,
                "week_start": week_start.isoformat(),
                "week_end": week_end.isoformat(),
                "count": len(records),
                "records": records,
            },
        )
    except Exception as e:
        return JSONResponse(
            status_code=400, content={"message": f"Error retrieving records: {str(e)}"}
        )


@js_ih_router.get("/js-ih-1/all")
async def get_all_js_ih_records(request: Request):
    """Get all records from JS-IH-1 collection"""
    try:
        cursor = request.app.state.js_ih_coll.find().sort("date", 1)

        records = []
        async for doc in cursor:
            records.append(
                {
                    "id": str(doc["_id"]),
                    "date": doc["date"].isoformat(),
                    "number": doc["number"],
                }
            )

        return JSONResponse(
            status_code=200, content={"count": len(records), "records": records}
        )
    except Exception as e:
        return JSONResponse(
            status_code=400, content={"message": f"Error retrieving records: {str(e)}"}
        )
