# API Documentation for Splitwise Agent

## Overview

This API provides endpoints for processing receipts and managing expenses using the Splitwise platform. It allows users to upload receipt images, create expenses, and retrieve groups and friends from Splitwise.

## Endpoints

### 1. Process Receipt

- **URL**: `/receipts/process`
- **Method**: `POST`
- **Request**:
  - **File**: UploadFile (receipt image)
- **Response**:
  - **Status**: success
  - **Data**: Extracted information from the receipt
- **Example**:
  ```json
  {
    "status": "success",
    "data": {'vendor': {'name': 'Costco Wholesale', 'address': 'Greenville, SC (Store #1005)', 'phone': None, 'category': 'Retail'}, 'transaction': {'date': '2019-03-31', 'time': '10:31 AM', 'receipt_number': None}, 'items': [{'name': 'Boneless/Skinless Chicken Breast', 'quantity': 1, 'unit_price': 22.1, 'total_price': 22.1, 'category': 'Meat'}, {'name': 'Grape Tomatoes', 'quantity': 1, 'unit_price': 5.99, 'total_price': 5.99, 'category': 'Produce'}, {'name': 'Butter', 'quantity': 1, 'unit_price': 10.39, 'total_price': 10.39, 'category': 'Dairy'}], 'summary': {'subtotal': 38.48, 'tax_details': [{'type': 'Sales Tax', 'amount': 0.0}], 'discounts': [], 'total': 38.48}, 'payment': {'method': 'Costco Visa', 'card_last_4': None, 'status': None}}
  }
  ```

### 2. Create Expense

- **URL**: `/expenses`
- **Method**: `POST`
- **Request**:
  - **Description**: str
  - **Amount**: float
  - **Group ID**: Optional[int]
  - **Split Equally**: bool (default: true)
- **Response**:
  - **Status**: success
  - **Data**: Created expense details
- **Example**:
  ```json
  {
    "status": "success",
    "data": {
      // Created expense details
    }
  }
  ```

### 3. Get Groups

- **URL**: `/groups`
- **Method**: `GET`
- **Response**:
  - **Status**: success
  - **Data**: List of groups
- **Example**:
  ```json
  {
    "status": "success",
    "data": [
      // List of groups
    ]
  }
  ```

### 4. Get Friends

- **URL**: `/friends`
- **Method**: `GET`
- **Response**:
  - **Status**: success
  - **Data**: List of friends
- **Example**:
  ```json
  {
    "status": "success",
    "data": [
      // List of friends
    ]
  }
  ```

### 5. Get Expenses

- **URL**: `/expenses`
- **Method**: `GET`
- **Request**:
  - **Group ID**: Optional[int]
  - **Limit**: int (default: 20)
- **Response**:
  - **Status**: success
  - **Data**: List of recent expenses
- **Example**:
  ```json
  {
    "status": "success",
    "data": [
      // List of recent expenses
    ]
  }
  ```

## Authentication

- Ensure to include necessary authentication tokens in the headers for accessing the endpoints.

## Error Handling

- The API will return HTTP status codes for errors, along with a message detailing the issue.
