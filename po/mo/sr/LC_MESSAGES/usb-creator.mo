��    E      D  a   l      �     �  A     	   R     \  X   p  8   �               )  A   =       ,   �     �     �  (   �                          1     O     ^  X   b  �   �  e   W	  	   �	     �	  Q   �	     )
     0
  >   =
  ;   |
     �
     �
     �
     �
     �
  :     
   ?     J  o   S  !   �     �             2   :  f   m  *   �     �            �      W   �  B   *  Y   m     �     �     �     �               2  "   :     ]     n  3   �  %   �     �  �  �  2   �  \   �     T     e  �   �  U        n  $   �  4   �  g   �  ,   M  M   z     �     �  <   �          (     5  6   F  ;   }      �     �  �   �  �   �  �   z  
           �   -  
   �     �  g   �  n   K  %   �  :   �  &        B     O  Q   `     �     �  �   �  (   �  )   �  %     '   1  =   Y  �   �  G   #     k     r  )   �    �  �   �  �   P  �   �  1   �   #   �      �   !   �      !  0   0!     a!  J   p!     �!  2   �!  U   "  E   a"  %   �"     -                 D      4   +       	           >         :       *   %   @   8   &      6          E      ,           )   5       A       0   7       "                 (       /              1   =       '      
                     ?      3          2   .      9   ;                  !                        $   C   <          B                     #    An unknown error has occurred. Are you sure you want to remove the selected ISO from the device? Available Browse for ISO file Cannot add ISO from path: {}.
Please, remove the ISO path or browse for an existing ISO. Cannot find the target ISO file. Did you insert the USB? Clear the ISO field Copy ISO to USB... Copy of ISO failed. Could not unmount the device.
Please unmount the device manually. Create a multi-boot USB Create a multi-boot USB with the USB Creator Description Device Device is in use by another application. Error Execute Finished Gather ISO information... Given ISO path was not found. Hash mismatch. ISO ISO too large for FAT formatted USB (max 4GB).
Format the USB to exFAT, NTFS, ext4, etc. If the ISO did not boot with automatic distribution name detection, you manually select the appropriate distribution name from the "Manual" drop down menu. If you still cannot boot your ISO you can configure the menu on your flash drive: /boot/grub/grub.cfg Important Install Grub... Make sure you backed up all important data from the flash drive before you start. Manual No Partition No partition found.
Please format the USB before you continue. Note: a fat32 partition can not hold files larger than 4GB. Partition device Prepare copy of ISO... Refresh device list Remove Required See "man usb-creator" for a list of all available options. Select ISO Terminal The USB Creator is a tool to help users to create a bootable flash drive with multiple Linux operating systems. The USB was successfully written. The device has no partition. The device is not detachable. The device was not found. There is not enough space available on the device. There is not enough space available on the pen drive.
Please, remove unneeded files before continuing. This will remove all data from the device. USB USB Creator USB Creator Help USB Creator expects a USB pen drive with a single fat32 partition or a 100MB fat32 boot partition and a second partition for the ISOs in the file system format of your choosing. USB Creator has failed with the following unexpected error. Please submit a bug report! USB Creator requires authentication to install Grub on your device Unable to determine the distribution name.
Select a distribution in the 'Manual' section. Unable to mount the device. Unexpected error Unmount Unmount device Unpacking ISO... Verify hash of ISO... Version Write a single ISO to USB using dd Write single ISO Wrong arguments were passed. You can also use the USB Creator from the terminal. You can now safely remove the device. Your ISO is not booting? Project-Id-Version: usb-creator
Report-Msgid-Bugs-To: 
PO-Revision-Date: 2020-11-19 13:22+0000
Last-Translator: Slobodan Simić <slsimic@gmail.com>
Language-Team: Serbian (http://www.transifex.com/abalfoort/usb-creator/language/sr/)
Language: sr
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Plural-Forms: nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2);
 Десила се непозната грешка. Заиста желите да уклоните изабрани ИСО са уређаја? Доступно Тражи ИСО фајл Не могу да додам ИСО са путање: {}.
Уклоните путању или пронађите постојећи ИСО фајл. Не могу да нађем ИСО фајл. Јесте ли убацили УСБ? Очисти ИСО поље Копирам ИСО на УСБ... Неуспело копирање ИСО фајла. Не могу да демонтирам уређај.
Уређај демонтирајте ручно. Прави вишесистемски УСБ Прави вишесистемски УСБ са УСБ ствараоцем Опис Уређај Уређај користи друга апликација. Грешка Изврши Завршено Прикупљам податке ИСО фајла... Наведена ИСО путања није нађена. Хеш се не поклапа. ИСО ИСО одраз је превелик за ФАТ форматирани УСБ (макс.4Gb)
Форматирајте УСБ на exFAT, NTFS, ext4 и сл. Ако се ИСО не подиже са аутоматским утврђивањем назива дистрибуције, ручно изаберите одговарајући назив из падајућег менија „Ручно“. Ако се и даље ИСО не подиже, мени можете подесити на флеш диску: /boot/grub/grub.cfg Важно Инсталирам ГРУБ... Проверите, пре него што почнете, да ли сте са флеша склонили све битне податке. Ручно Нема партиције Нема партиција.
Форматирајте УСБ пре него што наставите. Напомена: ФАТ32 партиција не може садржати фајлове веће од 4Gb. Партициониши уређај Припремам копирање ИСО одраза... Освежи листу уређаја Уклони Потребно Погледајте „man usb-creator“ за листу свих опција. Избор ИСО одраза Терминал УСБ стваралац је алат који омогућава корисницима да направе бутабилни флеш диск са више Линукс оперативних система. УСБ је успешно уписан. Уређај нема партиције. Уређај није уклоњив. Уређај није пронађен. Нема довољно простора на уређају. Нема довољно простора на флешу.
Уклоните непотребне фајлове пре настављања. Ово ће уклонити све податке са уређаја. УСБ УСБ стваралац Помоћ за УСБ ствараоца УСБ стваралац очекује УСБ диск са једном ФАТ32 партицијом или 100МБ ФАТ32 бут партицијом и другом партицијом за ИСО фајлове форматирану по вашем избору. УСБ стваралац није успео уз следећу неочекивану грешку. Пријавите грешку! УСБ стваралац захтева аутентификацију због инсталације ГРУБ-а на уређај Не могу да погодим дистрибуцију на основу ИСО фајла.
Изаберите дистрибуцију у одељку „Ручно“. Не могу да монтирам уређај. Неочекивана грешка Демонтирај Демонтирај уређај Распакујем ИСО... Проверавам хеш ИСО фајла... Верзија Уписује један ИСО одраз помоћу dd наредбе Упиши један ИСО Погрешни аргументи су дати. УСБ ствараоца можете користити и из терминала. Сада можете безбедно уклонити уређај. Ваш ИСО се не подиже? 