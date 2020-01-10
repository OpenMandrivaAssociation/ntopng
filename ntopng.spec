Summary:	A next generation Network and traffic analyzer
Name:		ntopng
Version:	2.4
Release:	2
License:	GPLv3
Group:		Monitoring
URL:		http://www.ntop.org
Source0:	https://github.com/ntop/ntopng/archive/%{version}.tar.gz
Source1:	ntopng.conf
Source2:	ntopng.service
Source3:	ntopng.sysconfig
Source4:	ntopng.tmpfiles.d
Patch0:		use-system-ndpi.patch
Patch1:		ntopng-2.0-ntop-running-user.diff
BuildRequires:	GeoIP-devel
BuildRequires:	pkgconfig(glib-2.0)
BuildRequires:	pkgconfig(hiredis)
BuildRequires:	pkgconfig(libxml-2.0)
BuildRequires:	json-c-devel
BuildRequires:	libpcap-devel
BuildRequires:	libxml2-devel
BuildRequires:	lua-devel
BuildRequires:	luajit-devel
BuildRequires:	openssl-devel
BuildRequires:	pkgconfig(libndpi) >= 1.5
BuildRequires:	pkgconfig(mariadb)
BuildRequires:	redis
BuildRequires:	rrdtool-devel
BuildRequires:	sqlite3-devel
BuildRequires:	wget
BuildRequires:	zeromq-devel >= 3.2.4
BuildRequires:	zlib-devel
BuildRequires:	curl-devel
Requires(post):  rpm-helper >= 0.24.8-1
Requires(preun): rpm-helper >= 0.24.8-1
Requires:	tcp_wrappers
Requires:	rrdtool
Requires:	geoip
Requires:	redis
Obsoletes:	ntop < 5.0.1

%description
ntopng is the next generation version of the original ntop.
It is a network packet traffic probe and collector that renders
network usage graphically, similar to what the popular top Unix
command does. It is based on libpcap and it has been written in a
portable way in order to virtually run on every Unix platform and on
Windows as well.

ntopng is easy to use and suitable for monitoring enterprise network
environments. A web browser is used to navigate through ntopng's
rendered web pages for viewing current traffic information and/or to
get a data dump of the collected network network status and statistics.
In the latter case, ntopng can be seen as a simple RMON-like agent with
an embedded web interface.

ntopng feature highlights:

* An intuitive web interface sporting numerous visuals and monitoring graphs.
* Show network traffic and IPv4/IPv6 active hosts.
* Analyse IP traffic and sort it according to the source/destination.
* Limited configuration and administration via the web interface.
* Reduced CPU and memory usage (this varies according to network size and
  traffic).
* Collection of a large number of hosts and network statistic values.
* Discover application protocols by leveraging nDPI (i.e., ntop’s Deep Packet
  Inspection Library).
* Report IP protocol usage sorted by protocol type.

%prep
%setup -q
%autopatch -p1

sed -i 's!/var/run/ntopng.pid!/var/run/ntopng/ntopng.pid!g' include/ntop_defines.h

%build
sh ./autogen.sh --noconfig

%serverbuild

%configure \
    --bindir=%{_sbindir} \
    --localstatedir=/var/lib

%make

%install

install -d %{buildroot}%{_datadir}/ntopng
install -d %{buildroot}%{_mandir}/man8
install -d %{buildroot}%{_sbindir}
install -d %{buildroot}%{_sysconfdir}/%{name}
install -d %{buildroot}%{_sysconfdir}/sysconfig
install -d %{buildroot}%{_unitdir}

install -m0755 ntopng %{buildroot}%{_sbindir}
install -m0644 ntopng.8 %{buildroot}%{_mandir}/man8

cp -r httpdocs %{buildroot}%{_datadir}/%{name}
cp -r scripts %{buildroot}%{_datadir}/%{name}

find %{buildroot}%{_datadir}/%{name} -name "*~"   | xargs rm -f
find %{buildroot}%{_datadir}/%{name} -name ".svn" | xargs rm -rf
find %{buildroot}%{_datadir}/%{name} -name ".git" | xargs rm -rf

install -d %{buildroot}%{_localstatedir}/lib/%{name}/rrd/{flows,graphics,interfaces}

install -m0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/%{name}/%{name}.conf
install -m0644 %{SOURCE2} %{buildroot}%{_unitdir}/%{name}.service
install -m0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/sysconfig/%{name}

# fix permissions
find %{buildroot}%{_datadir}/%{name}/httpdocs -type f -print0|xargs -0 chmod 644
find %{buildroot}%{_datadir}/%{name}/httpdocs -type d -print0|xargs -0 chmod 755

# dangling symlinks
rm -rf %{buildroot}%{_datadir}/%{name}/httpdocs/geoip
ln -s %{_datadir}/GeoIP %{buildroot}%{_datadir}/%{name}/httpdocs/geoip
ln -s %{_sysconfdir}/pki/tls/private/%{name}.pem %{buildroot}%{_datadir}/%{name}/httpdocs/ssl/%{name}-cert.pem

install -d %{buildroot}%{_localstatedir}/run/%{name}
mkdir -p %{buildroot}%{_tmpfilesdir}
install -m 0644 %{SOURCE4} %{buildroot}%{_tmpfilesdir}/%{name}.conf

%pre
%_pre_useradd %{name} %{_localstatedir}/lib/%{name} /bin/false

%post
%_post_service ntopng
%_create_ssl_certificate ntopng -b
chown %{name}:%{name} %{_sysconfdir}/pki/tls/private/ntopng.pem

%tmpfiles_create %{_tmpfilesdir}/%{name}

%preun
%_preun_service ntopng

%files
%doc README* doc/UserGuide.* doc/README*
%dir %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/%{name}.conf
%{_unitdir}/%{name}.service
%{_sbindir}/%{name}
%{_mandir}/man8/%{name}.8.*
%{_datadir}/%{name}/
%{_tmpfilesdir}/%{name}.conf
%attr(0750,ntopng,ntopng) %dir %{_localstatedir}/lib/%{name}
%attr(0755,ntopng,ntopng) %ghost %dir %{_localstatedir}/run/%{name}
