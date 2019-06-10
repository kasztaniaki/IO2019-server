from database.dbmodel import Pool, db, Software, OperatingSystem, User, Reservation

from datetime import timedelta, datetime as dt


# return list of most reserved pools with machine hours per pool: [("pool id", machine_hours)]
def most_reserved_pools(start_date=dt(2019, 1, 1), end_date=dt(2099, 12, 31)):
    pool_list = Pool.get_all_pools()
    stat_list = []

    for pool in pool_list:
        machine_hours = pool.get_machines_hours(start_date, end_date)
        stat_list.append((pool.ID, machine_hours))

    return stat_list


def most_reserving_users(start_date=dt(2019, 1, 1), end_date=dt(2099, 12, 31)):
    user_list = User.get_all_users()
    stat_list = []

    for user in user_list:
        machine_hours = user.get_machines_hours(start_date, end_date)
        stat_list.append((user.Email, machine_hours))

    return stat_list


# return amount of hours, when amount of available machines was below 10% of maximum count [("pool id", hours)]
def pools_bottleneck(start_date=dt.now(), end_date=(dt.now()+timedelta(days=7)), interval=1800, bottleneck=0.9):
    # interval in seconds
    # bottleneck is percentage

    if (end_date - start_date).days > 400:  # server would choke on this operation
        raise ValueError("Too huge delta time. Maximum is 400 days.")

    pool_list = Pool.get_all_pools(only_enabled=True)
    stat_list = []

    for pool in pool_list:
        date = start_date
        bottleneck_time = 0

        while (end_date - date).total_seconds() > 0:
            machine_usage = 1 - pool.available_machines(date, date+timedelta(seconds=(interval-1))) / pool.MaximumCount
            if machine_usage > bottleneck:
                bottleneck_time += interval/3600

            date = date + timedelta(seconds=interval)

        stat_list.append((pool.ID, int(bottleneck_time)))

    return stat_list


def top_bottlenecked_pools(start_date=dt.now(), end_date=(dt.now()+timedelta(days=7)), bottleneck=0.9):
    stat_list = pools_bottleneck(start_date, end_date, bottleneck=bottleneck)

    i = 0
    while i < stat_list.__len__():
        if stat_list[i][1] == 0:
            stat_list.remove(stat_list[i])
            i -= 1
        i += 1

    stat_list.sort(key=take_second_element, reverse=True)
    return stat_list[:5]


def top_unused_pools(start_date=dt.now(), end_date=(dt.now()+timedelta(days=7)), max_usage=0.5):
    stat_list = pools_bottleneck(start_date, end_date, bottleneck=max_usage)
    unused_pools = []

    for pool in stat_list:
        if pool[1] == 0:
            unused_pools.append(pool[0])

    return unused_pools


def take_second_element(elem):
    return elem[1]
