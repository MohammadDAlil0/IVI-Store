# IVI Store Project

This project is an e-commerce project. It enables customers to browse and shop products from the store, place orders, and discover new products and offers. The platform provides a way for searching using images and sementic titles.

## Table of Contents

- [Requirements](#requirements)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [API Endpoints In Postman](#api-endpoints-in-postman)

## Requirements

To run this project, you will need:

- Python 3.8+

## Getting Started

### Prerequisites

Make sure you have Python 3.8+ and MongoDB installed on your machine.

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/MohammadDAlil0/DCoffee
    ```

2. Install dependencies:

    ```bash
    cd IVI-Store
    pip install -r requirements.txt
    ```

3. Set up environment variables:

    Create a `.env` file in the root directory of the project and provide the following variables:

    ```bash
    STRIPE_API_KEY="your-stripe-key"
    SQL_ALCHEMY_DATABASE_URL ="sqlite:///./schemas.db"
    MONGO_DB_URL="your-mongodb-URL"
    LOCAL_URL="http://localhost:5173"

    SERVER_METADATA_URL="https://accounts.google.com/.well-known/openid-configuration"
    CLIENT_ID="your-google-client-ID"
    ```

4. Start the server:

    ```bash
    uvicorn main:app --reload
    ```

    The server should now be running on [http://localhost:8000](http://localhost:8000).

### API Endpoints In Postman

You can use and see the APIs using Swagger via this link: [http://localhost:4000/docs](http://documenter.getpostman.com/view/27420685/2sA3e2gVcJ](https://localhost:4000/docs)
