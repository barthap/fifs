clear; close all;
table = readtable('sensors_data.csv');
raw = table2array(table);

t = raw(:, 1);
gyro = raw(:, 2:4);
acc = raw(:, 5:7);
mag = raw(:, 8:10);
mag_unc = raw(:, 11:13);
rot = raw(:, 14:16);

% radiany na stopnie
rot = rot .* 180 / pi;

subplot(4,1,1)
plot(t, acc, 'linewidth', 2)
xlabel('t [s]')
ylabel('wartosc')
legend('X', 'Y', 'Z')
title('Akcelerometr')

subplot(4,1,2)
plot(t, mag, 'linewidth', 2)
xlabel('t [s]')
ylabel('wartosc')
legend('X', 'Y', 'Z')
title('Magnetometr')

subplot(4,1,3)
plot(t, gyro, 'linewidth', 2)
xlabel('t [s]')
ylabel('wartosc')
legend('X', 'Y', 'Z')
title('Żyroskop')

subplot(4,1,4)
plot(t, rot, 'linewidth', 2)
xlabel('t [s]')
ylabel('kąt [deg]')
legend('alpha', 'beta', 'gamma')
title('Kąty')
