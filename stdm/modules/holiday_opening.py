from stdm.modules.opening import component as opening
from stdm.modules.holiday import component as holiday

opening.add_module(holiday, 'holiday')
opening.add_transition("acknowledge_share_pos", "holiday.start", '&holiday.holiday_t', [])
opening.add_transition("acknowledge_share_neg", "holiday.start", '&holiday.holiday_t', [])
opening.add_transition("acknowledge_decline_share", "holiday.start", '&holiday.holiday_t', [])

opening.finalize()

if __name__ == '__main__':

    i = input('U: ')
    while True:
        arg_dict = {"prev_conv_date": "2020-1-8 16:55:33.562881", "username": "sarah"}
        arg_dict2 = {"prev_conv_date": "2019-12-12 16:55:33.562881", "username": "sarah"}
        arg_dict3 = {"prev_conv_date": "2019-12-12 16:55:33.562881", "username": None}
        arg_dict4 = {"prev_conv_date": None, "stat": "Ive met quite a few people with your name recently."}
        if i == "hello":
            arg_dict["request_type"] = "LaunchRequest"
            arg_dict2["request_type"] = "LaunchRequest"
            arg_dict3["request_type"] = "LaunchRequest"
            arg_dict4["request_type"] = "LaunchRequest"

        using = arg_dict2
        opening.vars().update({key: val for key, val in using.items() if val is not None})

        confidence = opening.user_transition(i) / 10 - 0.3
        print(opening.state(), opening.vars())
        print('({}) '.format(confidence), opening.system_transition())
        i = input('U: ')