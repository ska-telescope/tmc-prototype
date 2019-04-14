from tango import DeviceProxy

# Creating DeviceProxy for Alarm Handler device
alarmHandler_proxy = DeviceProxy("alarmhandler/1/1")

# Configure Alarms on DishMaster WindSpeed attribute
alarmHandler_proxy.command_inout("Load", "tag=alertDish1WindSpeed;"
                                         "formula=(mid_d0001/elt/master/WindSpeed > 10);"
                                         "on_delay=0;off_delay=0;priority=fault;"
                                         "shlvd_time=2;group=gr_all;message=Dish1 Wind speed exceeded;"
                                         "on_command=mid_d0001/elt/master/SetStowMode;enabled=1" )
alarmHandler_proxy.command_inout("Load", "tag=alertDish2WindSpeed;"
                                         "formula=(mid_d0002/elt/master/WindSpeed > 10);"
                                         "on_delay=0;off_delay=0;priority=fault;"
                                         "shlvd_time=2;group=gr_all;message=Dish2 Wind speed exceeded;"
                                         "on_command=mid_d0002/elt/master/SetStowMode;enabled=1" )
alarmHandler_proxy.command_inout("Load", "tag=alertDish3WindSpeed;"
                                         "formula=(mid_d0003/elt/master/WindSpeed > 10);"
                                         "on_delay=0;off_delay=0;priority=fault;"
                                         "shlvd_time=2;group=gr_all;message=Dish3 Wind speed exceeded;"
                                         "on_command=mid_d0003/elt/master/SetStowMode;enabled=1" )
alarmHandler_proxy.command_inout("Load", "tag=alertDish4WindSpeed;"
                                         "formula=(mid_d0004/elt/master/WindSpeed > 10);"
                                         "on_delay=0;off_delay=0;priority=fault;"
                                         "shlvd_time=2;group=gr_all;message=Dish4 Wind speed exceeded;"
                                         "on_command=mid_d0004/elt/master/SetStowMode;enabled=1" )
