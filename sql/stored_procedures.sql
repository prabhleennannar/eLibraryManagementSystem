//1.
USE `e_Library`;
DROP procedure IF EXISTS `list_all_books`;

DELIMITER $$
USE `eLibrary`$$
CREATE PROCEDURE `list_all_books` ()
BEGIN
	SELECT * FROM Books_Record;
END$$

DELIMITER ;


//2.
USE `eLibrary`;
DROP procedure IF EXISTS `eLibrary`.`add_new_book`;

DELIMITER $$
USE `eLibrary`$$
CREATE DEFINER=`root_user`@`%` PROCEDURE `add_new_book`(IN b_title Varchar(100), IN b_genre Varchar(45), IN b_author Varchar(100), IN qty int, IN b_status Varchar(45))
BEGIN
	insert into Books_Record(title, genre, author, quantity, status) values (b_title, b_genre, b_author, qty, b_status);
    commit;
END$$

DELIMITER ;


//3.
USE `eLibrary`;
DROP procedure IF EXISTS `get_book_based_on_id`;

DELIMITER $$
USE `eLibrary`$$
CREATE PROCEDURE `get_book_based_on_id` (IN b_id int)
BEGIN
	Select * from Books_Record where bookId = b_id;
END$$

DELIMITER ;


//4.
USE `eLibrary`;
DROP procedure IF EXISTS `update_book_qty`;

DELIMITER $$
USE `eLibrary`$$
CREATE PROCEDURE `update_book_qty` (IN b_id int, IN qty INT)
BEGIN
	Update Books_Record set quantity = qty where bookId = b_id;
    commit;
END$$

DELIMITER ;


//5.
USE `eLibrary`;
DROP procedure IF EXISTS `get_book_based_on_author`;

DELIMITER $$
USE `eLibrary`$$
CREATE PROCEDURE `get_book_based_on_author` (IN b_author Varchar(100))
BEGIN
	Select * from Books_Record where author = b_author;
END$$

DELIMITER ;


//6.
USE `eLibrary`;
DROP procedure IF EXISTS `get_book_based_on_title`;

DELIMITER $$
USE `eLibrary`$$
CREATE PROCEDURE `get_book_based_on_title` (IN b_title Varchar(100))
BEGIN
	Select * from Books_Record where title = b_title;
END$$

DELIMITER ;


//7.
USE `eLibrary`;
DROP procedure IF EXISTS `get_book_based_on_genre`;

DELIMITER $$
USE `eLibrary`$$
CREATE PROCEDURE `get_book_based_on_genre` (IN b_genre Varchar(45))
BEGIN
	Select * from Books_Record where genre = b_genre;
END$$

DELIMITER ;


//8.
USE `eLibrary`;
DROP procedure IF EXISTS `get_book_based_on_avail_qty`;

DELIMITER $$
USE `eLibrary`$$
CREATE PROCEDURE `get_book_based_on_avail_qty` ()
BEGIN
	Select * from Books_Record where quantity > 0;
END$$

DELIMITER ;


//9.
USE `eLibrary`;
DROP procedure IF EXISTS `get_issued_books_details_with_user_id`;

DELIMITER $$
USE `eLibrary`$$
CREATE PROCEDURE `get_issued_books_details_with_user_id` (IN user_id Varchar(130))
BEGIN
	Select * from Borrowed_Books_Details where userId = user_id and status = 'issued';
END$$

DELIMITER ;


//10.
USE `eLibrary`;
DROP procedure IF EXISTS `update_book_record_on_issue`;

DELIMITER $$
USE `eLibrary`$$
CREATE PROCEDURE `update_book_record` (IN book_id int, IN qty int, IN b_status Varchar(45))
BEGIN
	Update Books_Record set quantity = qty, status = b_status where bookId = b_id;
    commit;
END$$

DELIMITER ;


//11.
USE `eLibrary`;
DROP procedure IF EXISTS `issue_book`;

DELIMITER $$
USE `eLibrary`$$
CREATE PROCEDURE `issue_book` (IN user_id Varchar(130), IN book_id int, IN borrowDate Date, IN d_returnDate Date, IN fine int, IN b_status Varchar(45))
BEGIN
    insert into Borrowed_Books_Details(userId, bookId, borrowDate, defaultReturnDate, fine, status) values (user_id, book_id, borrowDate, d_returnDate, fine, b_status);
    commit;
END$$

DELIMITER ;


//12.
USE `eLibrary`;
DROP procedure IF EXISTS `search_book_by_book_id`;

DELIMITER $$
USE `eLibrary`$$
CREATE PROCEDURE `search_book_by_book_id` (IN book_id int)
BEGIN
	Select * from Books_Record where bookId = book_id;
END$$

DELIMITER ;


//13.
USE `eLibrary`;
DROP procedure IF EXISTS `get_issue_details_based_on_book_and_user`;

DELIMITER $$
USE `eLibrary`$$
CREATE PROCEDURE `get_issue_details_based_on_book_and_user` (IN user_id Varchar(130), IN book_id int)
BEGIN
	Select * from Borrowed_Books_Details where userId=user_id and bookId=book_id and status="issued";
END$$

DELIMITER ;


//14.
USE `eLibrary`;
DROP procedure IF EXISTS `return_book`;

DELIMITER $$
USE `eLibrary`$$
CREATE PROCEDURE `return_book` (IN user_id Varchar(130), IN book_id int, IN actual_returnDate Date, IN b_fine int)
BEGIN
	Update Borrowed_Books_Details set actualReturnDate = actual_returnDate, fine = b_fine, status = 'returned' where userId = user_id and bookId = book_id;
    commit;
END$$

DELIMITER ;


//15.
USE `eLibrary`;
DROP procedure IF EXISTS `get_user_issued_books`;

DELIMITER $$
USE `eLibrary`$$
CREATE PROCEDURE `get_user_issued_books` (IN user_id Varchar(130))
BEGIN
	SELECT br.bookId, br.title, br.genre, br.author, bbd.borrowDate, bbd.defaultReturnDate, bbd.status
    FROM Books_Record as br ,Borrowed_Books_Details as bbd WHERE  br.bookId = bbd.bookId
	AND bbd.status='issued' and bbd.userId=user_id;
END$$

DELIMITER ;


//16.
USE `eLibrary`;
DROP procedure IF EXISTS `get_user_returned_books`;

DELIMITER $$
USE `eLibrary`$$
CREATE PROCEDURE `get_user_returned_books` (IN user_id Varchar(130))
BEGIN
	SELECT br.bookId, br.title, br.genre, br.author, bbd.borrowDate, bbd.defaultReturnDate, bbd.actualReturnDate, bbd.fine, bbd.status
    FROM Books_Record as br ,Borrowed_Books_Details as bbd WHERE  br.bookId = bbd.bookId
	AND bbd.status='returned' and bbd.userId=user_id;
END$$

DELIMITER ;


//17.
USE `eLibrary`;
DROP procedure IF EXISTS `get_issued_book_based_on_book_id`;

DELIMITER $$
USE `eLibrary`$$
CREATE PROCEDURE `get_issued_book_based_on_book_id` (IN b_id int)
BEGIN
	Select bookId, userId, status from Borrowed_Books_Details where bookId = b_id and status = 'issued';
END$$

DELIMITER ;


//18.
USE `eLibrary`;
DROP procedure IF EXISTS `eLibrary`.`deactivate_book`;

DELIMITER $$
USE `eLibrary`$$
CREATE DEFINER=`root_user`@`%` PROCEDURE `deactivate_book`(IN b_id int)
BEGIN
	Update Books_Record set status = 'inactive', quantity = 0 where bookId=b_id;
    commit;
END$$

DELIMITER ;
;









