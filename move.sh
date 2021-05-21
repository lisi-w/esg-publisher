for file in $(ls /p/user_pub/publish-queue/NCC-todo | head -n 10000)
do
  mv /p/user_pub/publish-queue/NCC-todo/$file /p/user_pub/publish-queue/CMIP6-maps-todo/
done
