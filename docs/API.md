
# SIS API Documentation

## Endpoint
`POST /v1/scan`

## Request Headers

## Request Body
```json
{
  "scan_id": "uuid",
  "files": [
    {
      "name": "main.tf",
      "type": "terraform",
      "content": "resource \"aws_s3_bucket\" \"example\" {}"
    }
  ]
}
