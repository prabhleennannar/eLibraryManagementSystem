def handler(event, context):
    requested_dtls = event['requested_details']
    issued_book_details = event['issued_book_details']

    issued_books_ids = []
    if issued_book_details:
        for issued_book_detail in issued_book_details:
            issued_books_ids.append(issued_book_detail.get('book_id'))

    requested_books_ids = requested_dtls.get('books_list')

    books_already_issued = []
    if issued_books_ids:
        books_already_issued = [book for book in requested_books_ids if book in issued_books_ids]

    if books_already_issued:
        event['is_eligible'] = False
        event['reason'] = 'book already issued'
        event['books_already_issued'] = books_already_issued

    else:
        event['is_eligible'] = True
        requested_details = []
        for book_id in requested_books_ids:
            requested_details.append({
                'book_id': book_id,
                'user_id': requested_dtls.get('user_id')
            })

        event['books_to_issue'] = requested_details

    return event
