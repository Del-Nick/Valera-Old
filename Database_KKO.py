import traceback
from Database import connecting, disconnecting


def all_data_kko(id):
    try:
        conn, cursor = connecting()
        cursor.execute('SELECT * FROM kko WHERE id = %s', (id,))
        data = cursor.fetchone()
        return data
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL all_data", _ex)
        return 'Не удалось загрузить базу данных. Я уже сообщил о проблеме разработчикам'
    finally:
        disconnecting(conn, cursor)


def add_new_user_kko(id, fio, name_from_vk):
    try:
        conn, cursor = connecting()
        cursor.execute(
            """INSERT INTO kko (id, name_from_vk, fio) VALUES(%s, %s, %s)""", (id, name_from_vk, fio,))
        conn.commit()

    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)

    finally:
        disconnecting(conn, cursor)


def delete_user_kko(id):
    try:
        conn, cursor = connecting()
        cursor.execute("""DELETE FROM kko WHERE id =  %s""", (id,))
        conn.commit()
        return True
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL quize_delete_date", _ex)
        return False
    finally:
        disconnecting(conn, cursor)


def add_group_kko(group, id):
    if 'м' in group.lower():
        course = int(group[0]) + 4
    else:
        course = int(group[0])

    try:
        conn, cursor = connecting()
        cursor.execute("""UPDATE kko SET (course, group_user) = (%s, %s) WHERE id = %s""", (course, group, id))
        conn.commit()

    except Exception as _ex:
        traceback.print_exc()

    finally:
        disconnecting(conn, cursor)


def add_subject_kko(subject, id):
    try:
        subjects = list(all_data_kko(id)[5])
    except:
        subjects = None

    if subjects is not None:
        subjects.append(subject)
    else:
        subjects = [subject]

    try:
        conn, cursor = connecting()
        cursor.execute("""UPDATE kko SET subjects = %s WHERE id = %s""", (subjects, id))
        conn.commit()

    except Exception as _ex:
        traceback.print_exc()

    finally:
        disconnecting(conn, cursor)


def check_subjects_kko(id):
    try:
        conn, cursor = connecting()
        cursor.execute('SELECT subjects FROM kko WHERE id = %s', (id,))
        data = cursor.fetchone()[0]
        if data is None:
            return []
        else:
            return data
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL all_data", _ex)
        return 'Не удалось загрузить базу данных. Я уже сообщил о проблеме разработчикам'
    finally:
        disconnecting(conn, cursor)

def add_answers(id, num_quest, answer):

    conn, cursor = connecting()
    cursor.execute(f'SELECT kko_{num_quest} FROM kko WHERE id = %s', (id,))
    record = cursor.fetchone()[0]

    if record is None:
        records = [answer]
    else:
        records = list(record)
        records.append(answer)

    try:
        conn, cursor = connecting()
        cursor.execute(f"""UPDATE kko SET kko_{num_quest} = %s WHERE id = %s""", (records, id))
        conn.commit()

    except:
        traceback.print_exc()

    finally:
        disconnecting(conn, cursor)


def add_rate_the_survey(answer, id):
    try:
        conn, cursor = connecting()
        cursor.execute("""UPDATE kko SET rate_the_survey = %s WHERE id = %s""", (answer, id))
        conn.commit()

    except Exception as _ex:
        traceback.print_exc()

    finally:
        disconnecting(conn, cursor)


def check_rate_the_survey(id):
    try:
        conn, cursor = connecting()
        cursor.execute("""SELECT rate_the_survey FROM kko WHERE id = %s""", (id,))
        data = cursor.fetchone()[0]
        return data

    except Exception as _ex:
        traceback.print_exc()

    finally:
        disconnecting(conn, cursor)


