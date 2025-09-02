To access data backup, from the **main menu** select **Utilities**, then choose **Data backup, upload and restore**.
___

Data can be backed up in two different ways on Skipperman.

- A data snapshot
- A full backup

# Data snapshot

Snapshots are stored locally on the Skipperman server, and are a good way to periodically save what you have done in case you do something stupid (since there is no undo function). To make a snapshot you can eithier click `Snapshot data` on the main menu page (in the top orange box header), or click the `Write a snapshot of the data now` button on the backup data utilities menu option. To restore a snapshot, click on the `Restore data from data snapshot` button on the backup data menu. 

Once a snapshot has been restored you can't go back to how the data was before the snapshot was taken (unless you already have a snapshot or full backup), so please bear this in mind.

Only the last 10 snapshots are kept.

# Full backup

A full backup creates a .zip file containing all the data which is then downloaded to your local machine. This can then be uploaded from the local machine. This is useful for testing and code development, and to take a copy of the data should something happen to the remote server.

# Data lock

A data lock occurs when someone starts saving something to Skipperman, and then something goes wrong. The system assumes they are still saving, and won't allow anyone else to do so. Normally this is cleared by the system automatically but if it isn't you can clear the data lock here.

# Clear on disk cache

The cache is used to speed up page loading. There is a slim possibility it could get corrupted and cause weird behaviour. Clearing it is a good step to clear any unusual data.
