%define packages_in_diags openssh openssh-server iproute psutils
%define _target_cpu @ARCH@
# Prevent stripping, python-bytecompiling etc. as this has been already done for the packages
%global __os_install_post %{nil}

# We need to be able to read /etc/sshd stuff so we use:
# needsrootforbuild

Name:          sb2-obs-diagnostics-@ARCH@-inject
Version:       1.0
Release:       1
AutoReqProv:   0
BuildRequires: rpm grep tar patchelf sed fakeroot
BuildRequires: %packages_in_diags
# We should build only on i586/i486 these packages, however
# ExclusiveArch: or ExcludeArch: do not work here, because after OBS starts building
# we set the _target_cpu above to e.g. armv7hl and then rpm declines to build the package.
Source101: precheckin.sh
Source200: sb2-obs-diagnostics-template-rpmlintrc
# no auto requirements - they're generated
License:       BSD
Summary:       SB2 OBS diagnostics

%description
This is a package providing tools to allow a remote shell into an OBS worker for
diagnostic purposes.
It provides %packages_in_diags which are used by build-vm
It is not intended to be used in a normal system!

%package -n sb2-obs-diagnostics-@ARCH@-dependency-inject
Summary: Dependency for sb2 host side

%description -n sb2-obs-diagnostics-@ARCH@-dependency-inject
This is a package providing %packages_in_diags for SB2 tools directory
It is not intended to be used in a normal system!

%prep

%build

%install

#set +x -e
mkdir -p %buildroot
rpm -ql %packages_in_diags > filestoinclude1
#/var/log contains lots of random data we don't need
sed -i -e '/\/var\/log/d' filestoinclude1
cat > filestoignore << EOF
/etc/shadow
/etc/gshadow
/etc/mtab
/usr/share/man
/root
/usr/bin/chfn
/usr/bin/chsh
/etc/securetty
/var/cache/ldconfig
/usr/libexec/pt_chown
/usr/lib/locale/locale-archive
/usr/sbin/build-locale-archive
/usr/sbin/tzdata-update
/etc/security/opasswd
/sbin/unix_update
/var/lock
/var/lock/subsys
EOF
grep -vf filestoignore filestoinclude1 | sort | uniq > filestoinclude2
# Copy files to buildroot and preserve permissions.
tar --no-recursion -T filestoinclude2 -cpf - | ( cd %buildroot && fakeroot tar -xvpf - ) > filesincluded

# Add back "/" prefix, add double quotes to protect file names with spaces, use %%dir directive for
# directories to prevent "File listed twice" warnings.
sed -i filesincluded -e '
    # First line is special - it is the root directory
    1s,^\./$,%%dir /,
    t
    # Lines ending with / are special - they are directory paths
    s,^\(.*\)/$,%%dir "/\1",
    t
    # Everything else
    s,^.*$,"/&",
    '
cat filesincluded

#overwite hosts file to avoid getting a random hostname
touch %buildroot/etc/sb2-obs-diagnostics-template

%files -f filesincluded
%defattr(-,root,root)

%files -n sb2-obs-diagnostics-@ARCH@-dependency-inject
%defattr(-,root,root)
/etc/sb2-obs-diagnostics-template
