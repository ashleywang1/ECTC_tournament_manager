FROM nginx:1.15

# RUN rm /etc/nginx/sites-enabled/default
#ADD sites-enabled/ /etc/nginx/sites-enabled
RUN rm /etc/nginx/nginx.conf
ADD sites-enabled/nginx.conf /etc/nginx/nginx.conf
