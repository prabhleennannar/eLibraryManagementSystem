import json
import boto3
import pymysql
import os

sm_client = boto3.client('secretsmanager')
mysql_secret = os.environ['mysql_secret']


def handler(event, context):
    try:
        response = sm_client.get_secret_value(
            SecretId=mysql_secret
        )
        database_secrets = json.loads(response['SecretString'])
        connection = pymysql.connect(host=database_secrets['host'], user=database_secrets['username'],
                                     passwd=database_secrets['password'], database=database_secrets['dbname'])

        cursor = connection.cursor()

        print("Creating tables!")

        cursor.execute(
            "CREATE TABLE `e_Library`.`Books_Record` (bookId INT NOT NULL AUTO_INCREMENT,title VARCHAR(100) NOT NULL,genre VARCHAR(45) NOT NULL,author VARCHAR(100) NOT NULL,quantity INT NOT NULL,status VARCHAR(45) NOT NULL, PRIMARY KEY (bookId));")
        print("Created Books_Record Table!")

        cursor.execute("Drop Table `e_Library`.`Borrowed_Books_Details`;")

        cursor.execute(
            "CREATE TABLE `e_Library`.`Borrowed_Books_Details` (`id` INT NOT NULL AUTO_INCREMENT,`userId` VARCHAR(130) NOT NULL,`bookId` INT NOT NULL,`borrowDate` DATE NOT NULL,`defaultReturnDate` DATE NOT NULL,`actualReturnDate` DATE NOT NULL,`fine` INT NOT NULL,`status` VARCHAR(45) NOT NULL,PRIMARY KEY (`id`),INDEX `bookId_idx` (`bookId` ASC) VISIBLE,CONSTRAINT `bookId` FOREIGN KEY (`bookId`) REFERENCES `e_Library`.`Books_Record` (`bookId`) ON DELETE NO ACTION ON UPDATE NO ACTION);")
        print("Created Borrowed_Books_Details Table!")

        print("\nCreating stored procedures!")

        cursor.execute("""
                        CREATE PROCEDURE `return_book`(IN user_id Varchar(130), IN book_id int, 
                        IN actual_returnDate Date, IN b_fine int) 
                        BEGIN 
                            Update Borrowed_Books_Details set actualReturnDate = actual_returnDate, fine = b_fine, 
                            status = 'returned' where userId = user_id and bookId = book_id; commit; 
                        END 
                        """)
        print("Created return_book!")

        cursor.execute("""
                        CREATE PROCEDURE `search_book_by_book_id`(IN book_id int)
                        BEGIN
                            Select * from Books_Record where bookId = book_id;
                        END
                      """)
        print("Created search_book_by_book_id!")

        cursor.execute("""
                        CREATE PROCEDURE `update_book_qty`(IN b_id int, IN qty INT, IN b_status Varchar(45))
                        BEGIN
        	                Update Books_Record set quantity = qty, status = b_status where bookId = b_id;
                            commit;
                        END
                    """)
        print("Created update_book_qty!")

        cursor.execute("""
                        CREATE PROCEDURE `update_book_record`(IN book_id int, IN qty int)
                        BEGIN
        	                Update Books_Record set quantity = qty where bookId = book_id;
                            commit;
                        END
                    """)
        print("Created update_book_record!")

        cursor.execute("""
                        CREATE PROCEDURE `update_book_record_on_issue`(IN book_id int, IN qty int)
                        BEGIN
        	                Update Books_Record set quantity = qty where bookId = book_id;
                            commit;
                        END
                    """)
        print("Created update_book_record_on_issue!")

        cursor.execute("""
                        CREATE PROCEDURE `get_user_issued_books`(IN user_id Varchar(130))
                        BEGIN
        	                SELECT br.bookId, br.title, br.genre, br.author, bbd.borrowDate, bbd.defaultReturnDate, bbd.status
                            FROM Books_Record as br ,Borrowed_Books_Details as bbd WHERE  br.bookId = bbd.bookId
        	                AND bbd.status='issued' and bbd.userId=user_id;
                        END
                    """)
        print("Created get_user_issued_books!")

        cursor.execute("""
                        CREATE PROCEDURE `get_user_returned_books`(IN user_id Varchar(130))
                        BEGIN
        	                SELECT br.bookId, br.title, br.genre, br.author, bbd.borrowDate, bbd.defaultReturnDate, bbd.actualReturnDate, bbd.fine, bbd.status
                            FROM Books_Record as br ,Borrowed_Books_Details as bbd WHERE  br.bookId = bbd.bookId
        	                AND bbd.status='returned' and bbd.userId=user_id;
                        END
                    """)
        print("Created get_user_returned_books!")

        cursor.execute("""
                        CREATE PROCEDURE `issue_book`(IN user_id Varchar(130), IN book_id int, IN borrowDate Date, IN d_returnDate Date, IN fine int, IN b_status Varchar(45))
                        BEGIN
                            insert into Borrowed_Books_Details(userId, bookId, borrowDate, defaultReturnDate, fine, status) values (user_id, book_id, borrowDate, d_returnDate, fine, b_status);
                        commit;
                        END
                    """)
        print("Created issue_book!")

        cursor.execute("""
                        CREATE PROCEDURE `list_all_books`()
                        BEGIN
        	                SELECT * FROM Books_Record;
                        END
                    """)
        print("Created list_all_books!")

        cursor.execute("""
                        CREATE  PROCEDURE `get_issued_book_based_on_book_id`(IN b_id int)
                        BEGIN
        	                Select bookId, userId, status from Borrowed_Books_Details where bookId = b_id and status = 'issued';
                        END
                    """)
        print("Created get_issued_book_based_on_book_id!")

        cursor.execute("""
                        CREATE PROCEDURE `get_issued_books_details_with_user_id`(IN user_id Varchar(130))
                        BEGIN
        	                Select * from Borrowed_Books_Details where userId = user_id and status = 'issued';
                        END
                    """)
        print("Created get_issued_books_details_with_user_id!")

        cursor.execute("""
                        CREATE PROCEDURE `get_issue_details_based_on_book_and_user`(IN user_id Varchar(130), IN book_id int)
                        BEGIN
        	                Select * from Borrowed_Books_Details where userId=user_id and bookId=book_id and status="issued";
                        END
                    """)
        print("Created get_issue_details_based_on_book_and_user!")

        cursor.execute("""
                        CREATE PROCEDURE `get_book_based_on_avail_qty`()
                        BEGIN
        	                Select * from Books_Record where quantity > 0;
                        END
                    """)
        print("Created get_book_based_on_avail_qty!")

        cursor.execute("""
                        CREATE PROCEDURE `get_book_based_on_genre`(IN b_genre Varchar(45))
                        BEGIN
        	                Select * from Books_Record where genre = b_genre;
                        END
                    """)
        print("Created get_book_based_on_genre!")

        cursor.execute("""
                        CREATE PROCEDURE `get_book_based_on_id`(IN b_id int)
                        BEGIN
        	                Select * from Books_Record where bookId = b_id;
                        END
                    """)
        print("Created get_book_based_on_id!")

        cursor.execute("""
                        CREATE PROCEDURE `get_book_based_on_title`(IN b_title Varchar(100))
                        BEGIN
        	                Select * from Books_Record where title = b_title;
                        END
                    """)
        print("Created get_book_based_on_title!")

        cursor.execute("""
                        CREATE PROCEDURE `add_new_book`(IN b_title Varchar(100), IN b_genre Varchar(45), IN b_author Varchar(100), IN qty int, IN b_status Varchar(45))
                        BEGIN
        	                insert into Books_Record(title, genre, author, quantity, status) values (b_title, b_genre, b_author, qty, b_status);
                            commit;
                        END
                    """)
        print("Created add_new_book!")

        cursor.execute("""
                        CREATE PROCEDURE `deactivate_book`(IN b_id int)
                        BEGIN
        	                Update Books_Record set status = 'inactive', quantity = 0 where bookId=b_id;
                            commit;
                        END
                    """)
        print("Created deactivate_book!")

        cursor.execute("""
                        CREATE PROCEDURE `get_book_based_on_author`(IN b_author Varchar(100))
                        BEGIN
        	                Select * from Books_Record where author = b_author;
                        END
                    """)
        print("Created get_book_based_on_author!")

        cursor.execute("SELECT routine_name FROM information_schema.routines WHERE routine_type = 'PROCEDURE' AND "
                       "routine_schema = 'e_Library';")
        result = cursor.fetchall()
        print(result)

    except Exception as e:
        print(e)

    return {
        'statusCode': 200,
        'body': json.dumps('Successfully created tables and stored procedures!')
    }
