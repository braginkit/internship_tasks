{
	requests = request_data.get_all()
	request = requests.groupBy{
 		it.id
	}.collect{ key, value ->
		value.max{ it.version }
	}.findAll{ req ->
 		req.status == 'opened' &&
		req.state == 'ready'
	}.max{
		it.priority
	}
	if (request == null)
		return null
 
	request.state = 'inprogress'
	request.assignee = login
	request.version += 1

	if ((request_data.get(reqiust.id)).version + 1 == request.version)
		request_data.upload(request)
	else return null // либо здесь можно вызвать рекурсивно эту же функцию
	                 // либо можно весь код выше поместить в цикл do .. while

	return request
}
