"""logged_in_user = session.get('logged_in_user')
        if not logged_in_user:
            return "Unauthorized", 401
        
        data = request.get_json()
        allowed_fields = ["name", "image"] 

        fields = {}
        for field in allowed_fields:
            if field in data:
                fields[field] = data[field]

        query = "SET "
        num_fields = len(fields)
        for index, (key, value) in enumerate(fields.items()):
            if value is not None:
                query += f"{key} = '{value}'"
                if index < num_fields - 1:
                    query += ", "

        result = db_block(update_exercise, query, id, logged_in_user)
        if result:
            return result
        else:
            return 404 """