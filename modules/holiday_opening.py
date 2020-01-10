from src.StateTransitionDialogueManager.composite_dialogue_flow import CompositeDialogueFlow
from modules import opening, holiday

if __name__ == '__main__':
    holiday_opening = CompositeDialogueFlow(opening.component, "opening")
    holiday_opening.add_module(holiday.component, "holiday")
    holiday_opening.add_transition("opening.acknowledge_share_pos", "holiday.start", '&holiday_t', [])
    holiday_opening.add_transition("opening.acknowledge_share_neg", "holiday.start", '&holiday_t', [])
    holiday_opening.add_transition("opening.acknowledge_decline_share", "holiday.start", '&holiday_t', [])


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
        holiday_opening.vars().update({key: val for key, val in using.items() if val is not None})

        confidence = holiday_opening.user_transition(i) / 10 - 0.3
        print(holiday_opening.state(), holiday_opening.vars())
        print('({}) '.format(confidence), holiday_opening.system_transition())
        i = input('U: ')