import mysql.connector


def main():
    mydb = mysql.connector.connect(
        host="10.105.131.198",
        user="root",
        port = 3306,
        passwd="checkoutchamp",
        database="checkout"
    )

    mycursor = mydb.cursor()
    
    while (True):
        print("Options:")
        print("0: Quit")
        print("1: Add new entry to the database")
        print("2: See all entries")
        print("3: See item given barcode")
        x = input()

        if int(x) == 0:
            break
        elif int(x) == 1:
            try:
                print("Enter the barcode:")
                barcode = input()
                print("Enter the item name:")
                name = input()
                print("Enter the item weight:")
                weight = input()
                print("Enter the price flag:")
                price_flag = input()
                print("Enter the item price:")
                price = input()
                sql = "INSERT INTO items(barcode_id, item_name, item_weight, price_flag, item_price) values(%s, %s, %s, %s, %s)"
                mycursor.execute(sql, (barcode, name, weight, price_flag, price))
                mydb.commit()
                print("Successfully added item to the database!")
            except Exception as e:
                print(e)
        elif int(x) == 2:
            try:
                sql = "SELECT * FROM items"
                mycursor.execute(sql)
                res = mycursor.fetchall()
                for row in res:
                    print(row)
            except Exception as e:
                print(e)
        elif int(x)== 3:
            try:
                sql = "SELECT * FROM items WHERE barcode_id = %s"
                print("Enter the barcode:")
                barcode = input()
                mycursor.execute(sql, (barcode,))
                res = mycursor.fetchone()
                print(res)
            except Exception as e:
                print(e)


if __name__ == "__main__":
    main()


#('100976376418', 'Onion', 0.7187, 1, 0.78)
#('228743639156', 'Apple', 0.5937, 1, 1.39)
#('684251937420', 'Lime', 0.175, 1, 1.99)
#('958302416784', 'Lemon', 0.225, 1, 1.99)
#('962418211103', 'Pineapple', 2.969, 1, 1.29)