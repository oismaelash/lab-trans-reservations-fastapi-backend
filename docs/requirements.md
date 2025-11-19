# Room Reservation System Requirements

## 1. Overview
Web system for meeting room reservation management with complete CRUD functionality and time conflict validations.

## 2. Data Model

### 2.1. Entity: Reservation

#### Required Fields:
- **local** (string, required): Room location
- **sala** (string, required): Room name/identification
- **data_inicio** (datetime, required): Reservation start date and time
- **data_fim** (datetime, required): Reservation end date and time
- **responsavel** (string, required): Name of the person responsible for the reservation

#### Optional Fields:
- **cafe** (boolean, optional): Indicates if coffee is needed
- **quantidade_cafe** (integer, optional): Coffee quantity (required if `cafe = true`)
- **descricao** (string, optional): Additional reservation description

#### System Fields:
- **id** (integer, auto-increment): Unique reservation identifier
- **created_at** (datetime): Record creation date
- **updated_at** (datetime): Last update date

## 3. API Endpoints

### 3.1. Reservation Listing
- **GET** `/api/reservas`
  - Returns list of all reservations
  - Support for filters (optional): by date, room, location, responsible person
  - Pagination (optional)

### 3.2. Reservation Details
- **GET** `/api/reservas/{id}`
  - Returns complete details of a specific reservation

### 3.3. Reservation Creation
- **POST** `/api/reservas`
  - Creates a new reservation
  - Validates time conflicts before creating
  - Returns 409 (Conflict) error if there is a conflict

### 3.4. Reservation Update
- **PUT/PATCH** `/api/reservas/{id}`
  - Updates an existing reservation
  - Validates time conflicts before updating
  - Returns 409 (Conflict) error if there is a conflict

### 3.5. Reservation Deletion
- **DELETE** `/api/reservas/{id}`
  - Removes a reservation
  - Returns deletion confirmation

## 4. Validations and Business Rules

### 4.1. Time Conflict Validation
- A reservation cannot have time overlap with another reservation in the same room
- Verify that `data_inicio` and `data_fim` do not overlap with existing reservations
- Consider only active reservations (not deleted)

### 4.2. Field Validations
- `data_inicio` must be before `data_fim`
- `data_inicio` and `data_fim` cannot be in the past (or allow according to business rule)
- If `cafe = true`, then `quantidade_cafe` is required and must be > 0
- All required fields must be filled

### 4.3. Format Validations
- Dates must be in ISO 8601 format or format accepted by the API
- Text fields must respect character limits

## 5. API Responses

### 5.1. HTTP Status Codes
- **200 OK**: Successful operation (GET, PUT, DELETE)
- **201 Created**: Reservation created successfully (POST)
- **400 Bad Request**: Invalid data or missing required fields
- **404 Not Found**: Reservation not found
- **409 Conflict**: Time conflict detected
- **500 Internal Server Error**: Internal server error

### 5.2. Response Format
- Success: Return JSON object with reservation data
- Error: Return JSON object with descriptive error message

