# 1.1.0

* Add new methods:
    * `pause`, `unpause`, `toggle_pause`: : Pause/Resume download queue.
    * `stop_all_downloads`: Abort all running downloads.
    * `restart_failed`: Restart all failed files.
    * `toggle_reconnect`: Toggle reconnect activation
    * `delete_finished`: Delete all finished files and completly finished packages.
    * `restart`: Restart pyload core.
    * `free_space`: Get available free space at download directory in bytes.
* Add pytest unit testing for login method
* Refactored `get_status` and `version` methods

# 1.0.3

* Change logging to debug

# 1.0.2

* username and password changed to mandatory arguments
* Make dataclasses subscriptable

# 1.0.1

* Fix login and get_status not raising InvalidAuth when unauthorized

# 1.0.0

* Initial commit
