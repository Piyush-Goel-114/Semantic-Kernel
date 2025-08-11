import requests

url = "TEAMS_WORKFLOW_URL"

payload = {
    "sender_name": "Alex",
    "sender_email": "alex@example.com",
    "subject": "Bulk Order Inquiry",
    "thread_text": "Alex: Hi Bob, I wanted to place a bulk order for our office expansion: 120 heavy-duty staplers, 120 A4 lined books, and 192 blue ballpoint pens. Could you provide your best pricing with any bulk discounts? We need delivery within 2-3 weeks.\n\nBob: Hi Alex, I can offer staplers at ₹100 each, books at ₹200 each, and pens at ₹10 each, totaling ₹37,920. Given the bulk quantity, Ill provide a 5 percent discount bringing your total to ₹36,024. Let me know your preferred delivery timeline and I can arrange within 10-15 business days.\n\nAlex: Thanks for the competitive pricing Bob. I need to know the stapler brand, if books are spiral-bound, and can you send pen samples for quality check? Our office renovation is delayed, so could we push delivery to first week of July instead? Also, whats your warranty and return policy?\n\nBob: We supply Kangaro HP-45 staplers, spiral-bound A4 books with hard covers, and Ill courier 5 Pilot BP-S pen samples tomorrow. July 1st delivery works perfectly - morning or afternoon slot? We offer 30-day returns and on-site quality inspection for bulk orders. Shall I prepare a formal quotation?\n\nAlex: Perfect Bob! Id like to confirm the order: 120 Kangaro staplers (₹12,000), 120 spiral books (₹24,000), 192 Pilot pens (₹1,920), total ₹36,024 after 5 percent discount. Delivery July 1st morning slot to Global Solutions Inc., Gurgaon. Please prepare quotation with payment terms, include GST number 06AABCS1234F1Z0, and arrange on-site inspection.\n\nBob: Excellent Alex! Order #PSL-2025-0847 confirmed with July 1st morning delivery and on-site inspection included. Payment terms: 50 percent advance (₹18,012), balance on delivery via bank transfer. Pen samples arriving Thursday via Blue Dart, formal quotation attached with bank details. Once youre satisfied with samples, send advance payment and your PO number. Thanks for choosing us!"
}

try:
    response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})

    if response.status_code == 200:
        try:
            result = response.json()
            print("✅ Response from Logic App:")
            print(result)
        except ValueError:
            print("⚠️ Received non-JSON response:")
            print(response.text)
    else:
        print(f"❌ Request failed with status {response.status_code}: {response.text}")

except Exception as e:
    print(f"🔥 Error occurred: {e}")
