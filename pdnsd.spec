%define srcver 1.2.6
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
License: GPL
Group:  Networking/Other
Source: http://www.phys.uu.nl/~rombouts/pdnsd/releases/pdnsd-%{ver}.tar.gz
Source1: %name.initscript
Source2: %name.conf
#Patch: %{name}-%{ver}.diff.bz2
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
#%patch -p2 -E

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
rm -rf "$RPM_BUILD_ROOT"
%makeinstall_std

mkdir -p %buildroot%_initrddir %buildroot%_sysconfdir/sysconfig
install -m 755 %SOURCE1 %buildroot%_initrddir/%name

cat > %buildroot%_sysconfdir/sysconfig/%name <<EOF
# You can define options to pass to %name daemon
# See %name man page (8)
OPTIONS=""
EOF

mkdir -p %buildroot%{cachedir}
mkdir -p %buildroot%{_localstatedir}/%name

mkdir -p %buildroot%{_sysconfdir}
install -m 644 %SOURCE2 %buildroot%{_sysconfdir}/%name.conf

%clean
rm -rf "$RPM_BUILD_ROOT"

%pre
%_pre_useradd %name %_localstatedir/%name /bin/true

%postun
%_postun_userdel %name

%post
# Creating ghost file
[ -f %_var/cache/pdnsd/pdnsd.cache ] || echo -n -e "pd11\0\0\0\0" > %_var/cache/pdnsd/pdnsd.cache


%files
%defattr(-,root,root)
%doc THANKS TODO AUTHORS README README.par NEWS ChangeLog
%doc doc/html doc/txt
%attr(644,root,root) %_sysconfdir/pdnsd.conf.sample
%attr(644,root,root) %config(noreplace) %_sysconfdir/pdnsd.conf
%attr(755,root,root) %config(noreplace) %_sysconfdir/sysconfig/%name
%attr(755,root,root) %config(noreplace) %_initrddir/%name
%_sbindir/pdnsd
%_sbindir/pdnsd-ctl
%_mandir/man8/pdnsd.8*
%_mandir/man8/pdnsd-ctl.8*
%_mandir/man5/pdnsd.conf.5*
%attr(755,pdnsd,pdnsd) %dir %{cachedir}
%attr(644,pdnsd,pdnsd) %ghost %{cachedir}/pdnsd.cache
%attr(755,pdnsd,pdnsd) %dir %_localstatedir/%name


