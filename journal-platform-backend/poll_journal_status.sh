#!/bin/bash

# Polling script for journal job status
JOB_ID="40b88733-8403-4160-aa00-920e5f25b1f8"
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidXNlcl9hYjlmNDdmOWEwODIiLCJleHAiOjE3NjE5Mzk2MzR9.FAP3MbIzX00AnMzSIC3BTKInf_RmTT5ftQn_gDBRiug"

echo "🔍 Starting to poll for journal completion..."
echo "📋 Job ID: $JOB_ID"
echo "⏰ Will poll every 30 seconds for up to 15 minutes"
echo ""

for i in {1..30}; do
  echo "📞 Poll attempt $i/30..."

  response=$(curl -s "http://localhost:8000/api/journals/status/$JOB_ID" \
    -H "Authorization: Bearer $TOKEN")

  echo "📄 Response: $response"

  if echo "$response" | grep -q '"status":"completed"'; then
    echo "✅ Journal creation completed successfully!"
    break
  elif echo "$response" | grep -q '"status":"error"'; then
    echo "❌ Journal creation failed!"
    break
  elif echo "$response" | grep -q '"detail"'; then
    echo "⚠️ Authentication error in status endpoint - checking backend logs..."
  fi

  if [ $i -eq 30 ]; then
    echo "⏰ Maximum polling time reached (15 minutes)"
  else
    echo "😴 Waiting 30 seconds before next poll..."
    sleep 30
  fi
done

echo ""
echo "🏁 Polling complete!"