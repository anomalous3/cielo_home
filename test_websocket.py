#!/usr/bin/env python3
"""Test script for Cielo Home websocket functionality."""

import asyncio
import json
import os
import sys
from datetime import datetime

import aiohttp
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration from environment
SESSION_ID = os.getenv('SESSION_ID')
TOKEN = os.getenv('TOKEN')
MAC_ADDRESS = os.getenv('MAC_ADDRESS')  # Your device's MAC address
APPLIANCE_ID = os.getenv('APPLIANCE_ID')  # Your appliance ID
USER_ID = os.getenv('USER_ID')

WSS_URL = "wss://apiwss.smartcielo.com/websocket/"
USER_AGENT = "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36"

async def test_websocket():
    """Test the websocket connection and temperature control."""
    
    if not all([SESSION_ID, TOKEN, MAC_ADDRESS, APPLIANCE_ID, USER_ID]):
        print("Error: Missing required environment variables in .env file:")
        print("Required: SESSION_ID, TOKEN, MAC_ADDRESS, APPLIANCE_ID, USER_ID")
        return
    
    headers = {
        "Host": "apiwss.smartcielo.com",
        "Cache-control": "no-cache", 
        "Pragma": "no-cache",
        "User-agent": USER_AGENT,
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(
                WSS_URL,
                headers=headers,
                params={
                    "sessionId": SESSION_ID,
                    "token": TOKEN,
                },
                origin="https://home.cielowigle.com",
                compress=15,
                autoping=False,
            ) as websocket:
                
                print("✅ Connected to websocket successfully!")
                
                # Create temperature increment message
                temp_inc_msg = {
                    "action": "actionControl",
                    "actionSource": "WEB",
                    "applianceType": "AC",
                    "macAddress": MAC_ADDRESS,
                    "deviceTypeVersion": "BL01",  # You might need to adjust this
                    "fwVersion": "3.0.0,3.0.0",  # You might need to adjust this
                    "applianceId": int(APPLIANCE_ID),
                    "actionType": "temp",
                    "actionValue": "inc",
                    "connection_source": 1,
                    "user_id": USER_ID,
                    "preset": 0,
                    "oldPower": "on",
                    "myRuleConfiguration": {"1": "1,0", "activeTemplates": {"1": 1, "ruleTemplates": 1}, "ruleTemplates": {"1": [1]}},
                    "actions": {
                        "power": "on",
                        "mode": "cool",
                        "fanspeed": "fanspeed",
                        "temp": "72",  # Current temperature
                        "swing": " ",
                        "swinginternal": "",
                        "followme": "off"
                    },
                    "mid": f"test-{int(datetime.now().timestamp())}",
                    "application_version": "1.3.2",
                    "ts": int(datetime.now().timestamp())
                }
                
                print("📤 Sending temperature increment command...")
                print(f"Message: {json.dumps(temp_inc_msg, indent=2)}")
                
                await websocket.send_json(temp_inc_msg)
                
                # Listen for response
                timeout = 10
                try:
                    msg = await asyncio.wait_for(websocket.receive(), timeout=timeout)
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        response = json.loads(msg.data)
                        print("📥 Received response:")
                        print(json.dumps(response, indent=2))
                    else:
                        print(f"Received non-text message: {msg.type}")
                except asyncio.TimeoutError:
                    print(f"⏰ No response received within {timeout} seconds")
                
                # Wait a moment, then send decrement command
                await asyncio.sleep(2)
                
                # Create temperature decrement message
                temp_dec_msg = temp_inc_msg.copy()
                temp_dec_msg["actionValue"] = "dec"
                temp_dec_msg["actions"]["temp"] = "73"  # Different current temp
                temp_dec_msg["mid"] = f"test-{int(datetime.now().timestamp())}"
                temp_dec_msg["ts"] = int(datetime.now().timestamp())
                
                print("📤 Sending temperature decrement command...")
                print(f"Message: {json.dumps(temp_dec_msg, indent=2)}")
                
                await websocket.send_json(temp_dec_msg)
                
                # Listen for response
                try:
                    msg = await asyncio.wait_for(websocket.receive(), timeout=timeout)
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        response = json.loads(msg.data)
                        print("📥 Received response:")
                        print(json.dumps(response, indent=2))
                    else:
                        print(f"Received non-text message: {msg.type}")
                except asyncio.TimeoutError:
                    print(f"⏰ No response received within {timeout} seconds")
                
                print("✅ Test completed!")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Cielo Home Websocket Test")
        print("========================")
        print("This script tests the websocket temperature control functionality.")
        print("")
        print("Required .env file variables:")
        print("SESSION_ID=your_session_id")
        print("TOKEN=your_access_token")
        print("MAC_ADDRESS=your_device_mac_address")
        print("APPLIANCE_ID=your_appliance_id")
        print("USER_ID=your_user_id")
        print("")
        print("Run: python test_websocket.py")
        sys.exit(0)
    
    asyncio.run(test_websocket())