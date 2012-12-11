%define srcver 1.2.9
%define release %mkrel 1
%define ver %{srcver}-par
# '-' are denied in %version
%define version %(echo '%ver' | sed 's/-/./')

# Force value, use --without to disable
%define _with_ipv6 1
%define _with_ntpl 1

%{?_without_ntpl: %{expand: %%define %_with_ntpl 0}}
%{?_without_ipv6: %{expand: %%define %_with_ipv6 0}}
%{?_without_poll: %{expand: %%define %_with_poll 0}}
%{?_without_underscores: %{expand: %%define %_with_underscores 0}}
%{?_without_tcpqueries: %{expand: %%define %_with_tcpqueries 0}}
%{?_without_debug: %{expand: %%define %_with_debug 0}}
%{?_without_isdn: %{expand: %%define %_with_isdn 0}}

%{!?cachedir: %{expand: %%global cachedir %_var/cache/pdnsd}}
%define conffile %{_sysconfdir}/pdnsd.conf

Summary: A caching dns proxy for small networks or dialin accounts
Name: pdnsd
Version: %{version}
Release: %{release}
License: GPLv3+
Group: Networking/Other
Source0: http://www.phys.uu.nl/~rombouts/pdnsd/releases/pdnsd-%{ver}.tar.gz
Source1: %name.initscript
Source2: %name.conf
URL: http://www.phys.uu.nl/~rombouts/pdnsd/index.html
Requires(pre): rpm-helper
Requires(postun): rpm-helper

%description
pdnsd is a proxy DNS daemon with permanent (disk-)cache and the ability
to serve local records. It is designed to detect network outages or hangups
and to prevent DNS-dependent applications like Netscape Navigator from hanging.

This is a customized version with modifications made by Paul A. Rombouts.
For a description of the changes see http://www.phys.uu.nl/~rombouts/pdnsd.html
and the file README.par in %{_docdir}/%{name}-%{version}

Source rpm support those options (--without options to disable):

--with ntpl %{?_with_ntpl: (activate)}: use the Native POSIX Thread Library (NPTL);
--with isdn %{?_with_isdn: (activate)}: enable isdn support;
--with ipv6 %{?_with_ipv6: (activate)}: enable ipv6 support;
--with poll %{?_with_poll: (activate)}: use the select(2) function instead of poll(2);
--with underscores %{?_with_underscores: (activate)}: built with underscores enabled;
--with tcp_queries %{?_with_underscores: (activate)}.

%prep
%setup -q -n %{name}-%{srcver}

%build
%configure \
	--with-cachedir="%{cachedir}" \
	%{?_with_isdn:--enable-isdn} \
	%{?_without_poll:--disable-poll} \
	%{?_with_nptl:--with-thread-lib=nptl} \
	%{?_with_underscores:--enable-underscores} \
	%{?_with_ipv6:--enable-ipv6} \
	%{?_with_tcpqueries:--enable-tcp-queries} \
	%{?_without_debug:--with-debug=0}

%make

%install
%makeinstall_std

mkdir -p %buildroot%_initrddir %buildroot%_sysconfdir/sysconfig
install -m 755 %SOURCE1 %buildroot%_initrddir/%name

cat > %buildroot%_sysconfdir/sysconfig/%name <<EOF
# You can define options to pass to %name daemon
# See %name man page (8)
OPTIONS=""
EOF

mkdir -p %buildroot%{cachedir}
mkdir -p %buildroot%{_localstatedir}/lib/%name

mkdir -p %buildroot%{_sysconfdir}
install -m 644 %SOURCE2 %buildroot%{_sysconfdir}/%name.conf

%pre
%_pre_useradd %name %_localstatedir/lib/%name /bin/true

%post
# Creating ghost file
[ -f %_var/cache/pdnsd/pdnsd.cache ] || echo -n -e "pd11\0\0\0\0" > %_var/cache/pdnsd/pdnsd.cache
%_post_service pdnsd

%preun
%_preun_service pdnsd

%postun
%_postun_userdel %name

%files
%defattr(-,root,root)
%doc THANKS TODO AUTHORS README README.par NEWS ChangeLog
%doc doc/html doc/txt
%attr(644,root,root) %_sysconfdir/pdnsd.conf.sample
%attr(644,root,root) %config(noreplace) %_sysconfdir/pdnsd.conf
%attr(644,root,root) %config(noreplace) %_sysconfdir/sysconfig/%name
%attr(755,root,root) %config(noreplace) %_initrddir/%name
%_sbindir/pdnsd
%_sbindir/pdnsd-ctl
%_mandir/man8/pdnsd.8*
%_mandir/man8/pdnsd-ctl.8*
%_mandir/man5/pdnsd.conf.5*
%attr(755,pdnsd,pdnsd) %dir %{cachedir}
%attr(644,pdnsd,pdnsd) %ghost %{cachedir}/pdnsd.cache
%attr(755,pdnsd,pdnsd) %dir %_localstatedir/lib/%name


%changelog
* Wed Mar 14 2012 Dmitry Mikhirev <dmikhirev@mandriva.org> 1.2.9.par-1mdv2011.0
+ Revision: 785009
- update to 1.2.9

* Fri Sep 04 2009 Thierry Vignaud <tv@mandriva.org> 1.2.7.par-2mdv2010.0
+ Revision: 430251
- rebuild

* Fri Sep 19 2008 Frederik Himpe <fhimpe@mandriva.org> 1.2.7.par-1mdv2009.0
+ Revision: 285993
- Update to version 1.2.7 for important security fixes:
  port randomisation fixing CVE-2008-1447 and a fix for a denial of
  service (issue 2 of SA31847: http://secunia.com/advisories/31847/)

* Wed Jul 30 2008 Thierry Vignaud <tv@mandriva.org> 1.2.6.par-3mdv2009.0
+ Revision: 255174
- rebuild
- kill re-definition of %%buildroot on Pixel's request

  + Pixel <pixel@mandriva.com>
    - adapt to %%_localstatedir now being /var instead of /var/lib (#22312)

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

* Thu Oct 18 2007 Olivier Thauvin <nanardon@mandriva.org> 1.2.6.par-1mdv2008.1
+ Revision: 99813
- 1.2.6-par


* Wed Jan 17 2007 Olivier Thauvin <nanardon@mandriva.org> 1.2.5.par-2mdv2007.0
+ Revision: 110032
- fix permission and daemon uid (thx to Antonio <freenix at libero.it>)
- provide a default config file
- bunzip initscript

* Mon Jan 08 2007 Olivier Thauvin <nanardon@mandriva.org> 1.2.5.par-1mdv2007.1
+ Revision: 106126
- 1.2.5
- Import pdnsd

* Tue May 02 2006 Olivier Thauvin <nanardon@mandriva.org> 1.2.4.par-2mdk
- %%mkrel (/me sucks, thanks misc)

* Tue May 02 2006 Olivier Thauvin <nanardon@mandriva.org> 1.2.4.par-1mdk
- 1.2.4-par
- update urls

* Thu May 13 2004 Olivier Thauvin <thauvin@aerov.jussieu.fr> 1.1.11.par-1mdk
- mdk adaptation

* Sun Feb 08 2004 Paul Rombouts <p.a.rombouts@home.nl>
- Remove obsolete source files after patching.

