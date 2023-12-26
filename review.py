import pymssql
import random
import string

def printDB(cur, names, columns):
    cnt=0
    block=150
    # find how many rows in cur
    call = cur.fetchall()
    total = len(call)
    for row in call:
        for i in range(len(columns)):
            if i==0:
                print(names[i]+":",row[i],end=" ")
            else:
                print("| "+names[i]+":",row[i],end=" ")
        cnt+=1
        print()
        if(cnt % block == 0):
            print(cnt, "out of", total, "records shown, press Enter to continue, type q and ENTER to return to main menu")
            # check whether it's an enter or escape
            if input().lower() == 'q':
                break
    if cnt==0:
        print("No record found!!!")
    else:
        print(cnt, "records shown in total") 

def searchBusiness():
    # enter minimum number of stars (1 to 5), leave empty if no such filter
    min_stars = input("Please enter minimum number of stars (1 to 5), leave empty if no such filter: ")
    # convert min_stars to int
    try:
        min_stars = float(min_stars)
        if(min_stars < 1 or min_stars > 5):
            print("No minimum number of stars filter will apply")
            min_stars = -1
        else:
            print("Minimum number of stars = ", min_stars , ", filter will apply")                
    except ValueError:
        print("No minimum number of stars filter will apply")
        min_stars = -1
    b_min_stars = (min_stars>0)
    city = input("Please enter city, leave empty if no such filter: ")
    b_city = (city != '')
    if b_city:
        print("City = ", city, ", filter will apply")
    else:
        print("No city filter will apply")
    name = input("Please enter name (or part of the name), leave empty if no such filter: ")
    b_name = (name != '')
    if b_name:
        print("Name (or part of the name) = ", name, ", filter will apply")
    else:
        print("No name filter will apply")
    # choose order by name, city, or number of starts
    print("Order by: 1. Name (or part of name) 2. City 3. Number of stars, leave empty means order by name")
    order = input("Please enter your choice: (1, 2, or 3): ")
    try:
        order = int(order)
        if(order < 1 or order > 3):
            order = 1
    except ValueError:
        order = 1
    if order==1:
        print("Order by name")
    elif order==2:
        print("Order by city")
    else:
        print("Order by number of stars")

    # query business
    sql = 'SELECT business_id, name, address, city, stars FROM dbo.business WHERE ' + ( 'stars >= ' + str(min_stars) if b_min_stars else '1=1') 
    sql += (' AND LOWER(city) = LOWER(\''+city+'\')' if b_city else ' AND 1=1') 
    sql += (' AND LOWER(name) LIKE LOWER(\'%'+name+'%\')' if b_name else ' AND 1=1') 
    sql += (' ORDER BY name' if order==1 else (' ORDER BY city' if order==2 else ' ORDER BY stars'))

    #print('sql = ', sql)
    return sql

def searchUser():
    # filter by name or part of name
    name = input("Please enter name (or part of the name), leave empty if no such filter: ")
    b_name = (name != '')
    if b_name:
        print("Name (or part of the name) = ", name, ", filter will apply") 
    else:
        print("No name filter will apply")
    b_review_count = True
    # enter review count
    review_count = input("Please enter minimum review count, leave empty if no such filter: ")
    try:
        review_count = int(review_count)
    except ValueError:
        b_review_count = False
    if b_review_count:
        print("Minimum review count >= ", review_count, ", filter will apply")
    else:
        print("No minimum review count filter will apply")
    #enter average stars
    b_stars = True
    stars = input("Please enter minimum average star (1 to 5), leave empty if no such filter: ")
    try:
        stars = float(stars)
        if(stars < 1 or stars > 5):
            b_stars = False
    except ValueError:
        b_stars = False
    if b_stars:
        print("Minimum average star = ", stars, ", filter will apply")
    else:
        print("No minimum average stars filter will apply")


    # query users, return id, name, review count, useful, funny, cool, average stars, and the date
    sql = "SELECT user_id, name, review_count, useful, funny, cool, average_stars, yelping_since FROM dbo.user_yelp WHERE "
    sql += ('LOWER(name) LIKE LOWER(\'%'+name+'%\')' if b_name else '1=1')
    if b_review_count:
        sql += ' AND review_count >= ' + str(review_count)
    if b_stars:
        sql += ' AND average_stars >= ' + str(stars)
    sql += ' ORDER BY name'
    #print('sql = ', sql)
    return sql

def makeFriend(conn, user_id):
    # enter friend's user_id
    friend_id = input("Please enter friend's user_id: ")
    if friend_id == user_id:
        print("You cannot be friends with yourself")
        return
    # query friend's user_id in database
    cur = conn.cursor()
    cur.execute('SELECT * from dbo.user_yelp where user_id = %s', friend_id)
    # if friend's user_id is not in database, ask user to enter again
    if cur.fetchone() == None:
        print("This user_id does not exist")
        return 
    # check whether user_id and friend_id are already friends
    cur.execute('SELECT * from dbo.friendship where user_id = %s and friend = %s', (user_id, friend_id))
    if cur.fetchone() != None:
        print("You are already friends with this user")
        return
    # check whether user_id has a friend
    cur = conn.cursor()
    cur.execute('SELECT * from dbo.friendship where user_id = %s', user_id)
    if cur.fetchone() == None:
        # insert user_id and friend_id into friendship table
        sql = 'INSERT INTO dbo.friendship (user_id, friend) VALUES (%s, %s)'
        #print('sql = ', sql)
        cur = conn.cursor()
        cur.execute(sql, (user_id, friend_id))
        conn.commit()
    else:
        # update friend of user_id to new friend's user_id
        sql = 'UPDATE dbo.friendship SET friend = %s WHERE user_id = %s'
        #print('sql = ', sql)
        cur = conn.cursor()
        cur.execute(sql, (friend_id, user_id))
        conn.commit()
    print("You successfully make friends with this user:", friend_id)
    return

def randomChar(count):
    # generate random string of length count
    # 1-9, a-z, A-Z, -, _
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits + '-' + '_') for _ in range(count))


def reviewBusiness(conn, user_id):
    # enter business_id
    business_id = input("Please enter business_id: ")
    # query business_id in database
    cur = conn.cursor()
    cur.execute('SELECT * from dbo.business where business_id = %s', business_id)
    # if business_id is not in database, ask user to enter again
    if cur.fetchone() == None:
        print("This business_id does not exist")
        return
    # enter stars from 1 to 5 integer
    stars = input("Please enter stars from 1 to 5: ")
    try:
        stars = int(stars)
        if(stars < 1 or stars > 5):
            print("Invalid stars")
            return
    except ValueError:
        print("Invalid stars")
        return
    review_id = randomChar(22)
    # insert review
    sql = 'INSERT INTO dbo.review (review_id, user_id, business_id, stars) VALUES (%s, %s, %s, %s)'
    # print('sql = ', sql)
    cur = conn.cursor()
    cur.execute(sql, (review_id, user_id, business_id, stars))
    conn.commit()
    print("You successfully review this business:", business_id, "with stars:", stars, "review_id:", review_id)

    check = False
    if(check):
        # calculate the total number of reviews of this business
        cur = conn.cursor()
        cur.execute('SELECT * from dbo.review R where R.business_id = %s AND R.date=(SELECT MAX(date) from dbo.review R2 where R2.user_id = R.user_id AND R2.business_id=R.business_id)', business_id)
        total = len(cur.fetchall())
        # fetch the total number of reviews from business table directly through review_count
        cur = conn.cursor()
        cur.execute('SELECT review_count from dbo.business where business_id = %s', business_id)
        review_count = cur.fetchone()[0]
        print("Total number of reviews of this business:", total, "review_count:", review_count)

        # calculate the average starts of this business
        cur = conn.cursor()
        cur.execute('SELECT stars from dbo.review R where business_id = %s AND R.date=(SELECT MAX(date) from dbo.review R2 where R2.user_id = R.user_id AND R2.business_id=R.business_id)', business_id)
        total_stars = 0
        for row in cur:
            total_stars += row[0]
        average_stars = total_stars / total
        # calculate the average stars from business table directly through stars
        cur = conn.cursor()
        cur.execute('SELECT stars from dbo.business where business_id = %s', business_id)
        stars = cur.fetchone()[0]
        print("Average stars of this business:", average_stars, "stars:", stars)

def main():

    conn = pymssql.connect(host='cypress.csil.sfu.ca', user='s_jnqian', password='aJq2gFF36JEMYPJJ', database='jnqian354')

    # first set user_id to empty
    user_id = ''

    # ask for user to enter user_id
    user_id = input("Please enter user_id: ")

    #query user_id in database
    cur = conn.cursor()
    cur.execute('SELECT * from dbo.user_yelp where user_id = %s', user_id)
    # if user_id is not in database, ask user to enter again
    while cur.fetchone() == None:
        user_id = input("Please enter user_id again: ")
        cur.execute('SELECT * from dbo.user_yelp where user_id = %s', user_id)

    print("Login successfully as user_id: " + user_id)

    while True:
        # show main menu 1. Search Business 2. Search Users 3. Make Friend 4. Review Business 5. Exit
        print("-----------------------")
        print("Main Menu")
        print("1. Search Business")
        print("2. Search Users")
        print("3. Make Friend")
        print("4. Review Business")
        print("5. Exit")
        # ask user to enter choice
        choice = input("Please enter your choice: ")
        # if choice is 1
        if choice == '5':
            break
        if choice == '1':
            sql = searchBusiness()
            cur = conn.cursor()
            cur.execute(sql, ())
            printDB(cur, ('business_id', 'name', 'address', 'city', 'stars'), ('business_id', 'name', 'address', 'city', 'stars'))        
        elif choice == '2':
            sql = searchUser()
            cur = conn.cursor()
            cur.execute(sql, ())
            printDB(cur, ('user_id', 'name', 'review_count', 'useful', 'funny', 'cool', 'average_stars', 'yelping_since'), ('user_id', 'name', 'review_count', 'useful', 'funny', 'cool', 'average_stars', 'yelping_since'))
        elif choice == '3':
            makeFriend(conn, user_id)
        elif choice == '4':
            reviewBusiness(conn, user_id)

    conn.close()


main()
