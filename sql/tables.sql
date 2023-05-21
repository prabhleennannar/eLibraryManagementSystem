CREATE TABLE `e_Library`.`Books_Record` (
  `bookId` INT NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(100) NOT NULL,
  `genre` VARCHAR(45) NOT NULL,
  `author` VARCHAR(100) NOT NULL,
  `quantity` INT NOT NULL,
  `status` VARCHAR(45) NOT NULL
  PRIMARY KEY (`bookId`));


CREATE TABLE `e_Library`.`Borrowed_Books_Details` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `userId` VARCHAR(130) NOT NULL,
  `bookId` INT NOT NULL,
  `borrowDate` DATE NOT NULL,
  `defaultReturnDate` DATE NOT NULL,
  `actualReturnDate` DATE NOT NULL,
  `fine` INT NOT NULL,
  `status` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `bookId_idx` (`bookId` ASC) VISIBLE,
  CONSTRAINT `bookId`
    FOREIGN KEY (`bookId`)
    REFERENCES `eLibrary`.`Books_Record` (`bookId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);
