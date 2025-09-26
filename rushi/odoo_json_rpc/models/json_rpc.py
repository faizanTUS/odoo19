import requests

url = "http://localhost:8888/json-call"
login_url = 'http://localhost:8888/json-call/user_authenticate'
logout_url = 'http://localhost:8888/json-call/user_logout'
headers = {
    'Content-Type': "application/json",
}

data = {
  "jsonrpc": "2.0",
  "params": {
	"login": "kazi",
  	"password": 'a',
  	"db": 'json_rpc_10',	 		
  }
}

response = requests.post(login_url,json=data, headers=headers)
response = response.json()

if response.get('result') and response.get('result').get('token'):
	token = str(response.get('result').get('token'))
	payload = {
	  "jsonrpc": "2.0",
	  "params": {
		    "token": token, 		
		    "model": "res.partner",	
		    "method": "create",
		    "args": 
			[{
				"name":"mustufa"
			}],
		    "context": {}
	  }
	}
	response = requests.post(url,json=payload, headers=headers)
	response = response.json()

	data = {
	  "jsonrpc": "2.0",
	  "params": {
 		"token": token, 		
	  }
	}

	
	response = requests.post(logout_url,json=payload, headers=headers)
	response = response.json()




for record in response.get('result'):
	new_order_line = []
	for order_line in record.get('order_line'):

		payload = {
		  "jsonrpc": "2.0",
		  "params": {
		  	"token":"b58dceb5f5b1fc68f7e47e97b4d67e0f73a32740d0115e54ecaac73b2c805333",
		    "model": "sale.order.line",	
		    "method": "search_read",
		    "args": 
		      [[("id","=",order_line)]]
		    ,
		    "context": {}
		  }
		} 
		rec=requests.post(url,json=payload, headers=headers)

		order = rec.json()
		for some in order['result']:

			if some.get('name') == 'Datacard':


				payload = {
						  "jsonrpc": "2.0",
						  "params": {
						  	"token":"b58dceb5f5b1fc68f7e47e97b4d67e0f73a32740d0115e54ecaac73b2c805333",
						    "model": "sale.order.line",	
						    "method": "write",
						    "args": 
						      [[order_line],{'product_uom_qty':1.0}] 
						    ,
						    "context": {}
						  }
						} 

				rec1=requests.post(url,json=payload, headers=headers)


				# print"ssssssssssssssss",some.get('name')
				# print"lllllllllllllll",some.get('product_uom_qty')
				some.update({'product_uom_qty':4.0})
				# print "qqqqqqqqqqqqqqqqqq",some
		new_order_line.append(rec.json().get('result')[0])
	record['order_line'] = new_order_line
	# print "22222222222222222",order_line






# print '11111111111111111', response
	

