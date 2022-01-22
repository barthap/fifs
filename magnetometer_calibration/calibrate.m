%% Wczytaj dane z kalibracji
% dane z wykładu
% load('mag3110_20Hz');

% dane z wykladu to mialy, moj skrypt tego nie zapisywal
% wiec wpisuje recznie
Ts = 0.05; 

table = readtable('magnetometer_data.csv');
raw_arr = table2array(table);

% Dane z czujnika nieskalibrowanego, w formacie identycznym
% jak B_meas z danych z wykładu
B_meas = raw_arr(:, 4:6)';    

% j.w. tylko dane skalibrowane przez system operacyjny telefonu
% uzyte do porownania wynikow kalibracji
B_meas_cal = raw_arr(:, 1:3)'; 



%% opcje algorytmu
mag = 47.31551;            % wartość pola magnetycznego w krakowie [µT]
n = length(B_meas);        % sprawdźmy gługość wektora mierzonego

%% Wypisz podstawowe informacje o danych
fprintf('\nCzęstotliwość próbkowania:\t%2.1f [Hz]\n',1/Ts);
fprintf('Liczba próbek: \t\t\t%d\n',n);
fprintf('Czas eksperymentu:\t\t%2.1f [min]\n',n*Ts/60);

%% Wybierzmy warunek początkowy optymalizacji
A0 = 1*eye(3);         % początkowa macierz diagonalna
b0 = mean(B_meas,2);        % początkowy offset równy średniej z pomiarów
x0 = [A0(1,1);A0(2,2);A0(3,3);0;0;0;b0]';   % wektor wartości początkowych

%% Dopasujmy optymalizacyjnie bias i macierz skośną
f = @(x)fitSphere(x, B_meas, mag);
options = optimset('TolX', 1e-10, 'MaxFunEvals', 300); % Opcje optymalizacji
[x,fval,exitflag,output] = fminsearch(f,x0,options);

%% Odzyskaj zoptymalizowaną macierz kalibracyjną i wektor offsetu
A = [x(1),x(4),x(6);  0,x(2),x(5);   0,0,x(3)];
b = x(7:9)';

%% Rozkoduj macierz kalibracyjną na wzmocnienia i kąty pomiędzy osiami
Ae=A'*A;
k = sqrt(diag(Ae));
K = diag(k);
T = inv(A*K);
alpha(1) = 180/pi*acos(T(1,2)*T(2,2) + T(1,3)*T(2,3));
alpha(2) = 180/pi*acos(T(2,3));
alpha(3) = 180/pi*acos(T(1,3));
fprintf('Wzmocnienie osi X:\t\t%1.2f\n',k(1));
fprintf('Wzmocnienie osi Y:\t\t%1.2f\n',k(2));
fprintf('Wzmocnienie osi Z:\t\t%1.2f\n',k(3));
fprintf('Kąt pomiądze osią X i Y:\t%3.2f°\n',alpha(1));
fprintf('Kąt pomiądze osią Y i Z:\t%3.2f°\n',alpha(2));
fprintf('Kąt pomiądze osią X i Z:\t%3.2f°\n',alpha(3));

%% Skalibruj pomiar
%B_cal = nan(3, n);

%B_meas = A*B_cal + b;  % obustronnie odejmuje b
%B_meas - b = A*B_cal;  % mnoże lewostronnie przez odwrocona macierz A
% B_cal = inv(A)*(B_meas - b);
B_cal = A\(B_meas - b);

% disp(A);
% disp(b);
% disp(x);


%% Oblicz wartości bezwzględne pomiaru i surowych danych
B_mag = sqrt(sum(B_meas.^2)); % obliczmy wartość bezwzględną surowych pomiarów
B_mag_cal = sqrt(B_cal(1,:).^2+B_cal(2,:).^2+B_cal(3,:).^2);

%% Narysujmy sfferę pomiarową
figure(), plot3(B_meas(1,:),B_meas(2,:),B_meas(3,:),'+-r');
hold on, grid on;
axis('equal'), box('on');
xlabel('B_x'), ylabel('B_y'), zlabel('B_z');
title('Elipsoidy pomiarowe magnetometru');
plot3(B_cal(1,:), B_cal(2,:), B_cal(3,:), '+-g');
[xs,ys,zs] = sphere;
sh = surf(mag*xs,mag*ys,mag*zs);
set(sh,'FaceColor',[0 0.1 0],'FaceAlpha',0);
plot3(B_meas_cal(1,:),B_meas_cal(2,:),B_meas_cal(3,:),'+-b');
legend('nieskalibrowane', 'skalibrowane', 'idealne', 'skalibrowane wg telefonu');

%% Narysujmy wartości bezwzględne skalibrowanego i nieskalibrowanego pomiaru
figure(), plot(B_mag,'r+');
hold on, grid on;
title('Wartość bezwzględna przed i po kalibracji');
xlabel('sample number'), ylabel('B magnitude [µT]');
plot(B_mag_cal,'g+');
legend('nieskalibrowane ||B||', 'skalibrowane ||B||');

%% Narysujmy wartości skalibrowanego i nieskalibrowanego pomiaru
len = min(300,length(B_meas));
figure(), plot(B_meas(:,1:len)','--');
hold on, grid on;
title('Wartość pomiaru przed i po kalibracji');
xlabel('sample number'), ylabel('B magnitude [µT]');
plot(B_cal(:,1:len)','linewidth',2);
legend('B_x nieskalibrowane', 'B_y nieskalibrowane', 'B_z nieskalibrowane', ...
       'B_x skalibrowane', 'B_y skalibrowane', 'B_z skalibrowane');


%+=========================================================================
%% Funkcja celu optymalizacji
%==========================================================================
% Pomiary opisane są elipsoidą B_meas[:,i]' * Q * B_meas[:,i] + u'*B_meas[:,i]+ k
% Q = inv(A)'*inv(A);
% u = -2*Q'*b;
% k = b'*Q*b-Mag^2;

function [f] = fitSphere(x, B_meas, mag)

f = 0;  % Zacznijmy od wyzerowania wartości funkcji celu

A = [x(1),x(4),x(6);  0,x(2),x(5);   0,0,x(3)];
b = x(7:9)';
iA = inv(A);
Q = iA'*iA;


for i=1:size(B_meas,2)
    h = B_meas(:,i);
    if(sum(~isnan(h)) == 3)
        f = f + (mag^2 - (h-b)' * Q * (h-b) )^2;
    end
end

end

